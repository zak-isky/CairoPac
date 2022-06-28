# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PurchaseRequest(models.Model):
    _name = 'purchase.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Purchase Request'

    name = fields.Char(string='Seq.', readonly=1, copy=False, default="New")
    active = fields.Boolean(string='Active', default=True, )
    request_date = fields.Date(string='Request Date', default=fields.Date.context_today, track_visibility='onchange')
    schedule_date = fields.Date(string='Schedule Date', track_visibility='onchange')
    department_id = fields.Many2one('hr.department', string='Department', compute="_compute_department", store=True)
    requester_id = fields.Many2one('res.users', default=lambda self: self.env.user, readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Cost Center',
                                          track_visibility='onchange')

    request_line_ids = fields.One2many('purchase.request.line', 'purchase_request_id', strinh='Items', copy=True)

    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('rejected', 'Rejected')],
                             default='draft', track_visibility='onchange')
    reject_reason = fields.Text(string='Reject Reason')
    purchase_order_count = fields.Integer(string='PO Count', compute='_get_purchase_order_count')
    purchase_requisition_count = fields.Integer(string='PA Count', compute='_get_purchase_requisition_count')
    total_cost = fields.Float('Total Cost', compute='_compute_func_total_cost')

    @api.onchange('requester_id')
    def _compute_department(self):
        for rec in self:
            rec.department_id = rec.requester_id.department_id

    @api.depends('request_line_ids')
    def _compute_func_total_cost(self):
        for rec in self:
            rec.total_cost = sum([line.total_cost for line in rec.request_line_ids])

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code("purchase.request.sequence") or "New"
        return super(PurchaseRequest, self).create(vals_list)

    def unlink(self):
        for request in self:
            if request.state not in ['draft', 'rejected']:
                raise ValidationError(_('You can only delete draft or rejected requests !'))
        return super(PurchaseRequest, self).unlink()

    def action_confirm_request(self):
        self.ensure_one()
        if not self.request_line_ids:
            raise ValidationError(_('You need to add items before confirm !'))
        self.state = 'confirmed'

    def action_reject_request(self):
        self.ensure_one()
        if not self.reject_reason:
            raise ValidationError(_('You need to add reject reason !'))
        self.state = 'rejected'

    def action_set_request_to_draft(self):
        self.ensure_one()
        self.state = 'draft'

    def _get_purchase_order_count(self):
        self.ensure_one()
        self.purchase_order_count = self.env['purchase.order'].sudo().search_count(
            [('purchase_request_id', '=', self.id)])

    def action_view_purchase_orders(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_form_action")
        purchase_order_objects = self.env['purchase.order'].search([('purchase_request_id', '=', self.id)])
        action['domain'] = [('id', 'in', purchase_order_objects.ids)]
        return action

    def action_create_purchase_order(self):
        self.ensure_one()
        purchase_order_line_vals = []
        for line in self.request_line_ids:
            purchase_order_line_vals.append({
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_qty': line.product_qty,
                'product_uom': line.product_uom_id.id,
                'price_unit': line.product_id.list_price,
                'date_planned': fields.Date.today(),
                'taxes_id': False,
                'purchase_request_line_id': line.id,
            })
        form_view_id = self.env.ref('purchase.purchase_order_form')
        context = {

            'default_seq': self.name,
            'default_requester_id': self.requester_id.id,
            'default_department_id': self.department_id.id,
            'default_order_line': purchase_order_line_vals,
            'default_purchase_request_id': self.id,
        }
        print(context)
        action = {
            'name': _('Create PO'),
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'view_id': form_view_id.id,
            'type': 'ir.actions.act_window',
            'context': context,
        }
        return action

    def _get_purchase_requisition_count(self):
        self.ensure_one()
        self.purchase_requisition_count = self.env['purchase.requisition'].sudo().search_count(
            [('purchase_request_id', '=', self.id)])

    def action_view_purchase_requisitions(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("purchase_requisition.action_purchase_requisition")
        purchase_order_objects = self.env['purchase.requisition'].search([('purchase_request_id', '=', self.id)])
        action['domain'] = [('id', 'in', purchase_order_objects.ids)]
        return action

    def action_create_purchase_requisition(self):
        self.ensure_one()
        purchase_requisition_line_vals = []
        for line in self.request_line_ids:
            purchase_requisition_line_vals.append({
                'product_id': line.product_id.id,
                'product_qty': line.product_qty,
                'qty_ordered': line.product_qty,
                'product_uom_id': line.product_uom_id.id,
                'account_analytic_id': self.analytic_account_id.id or False,
                'schedule_date': fields.Date.today(),
            })
        form_view_id = self.env.ref('purchase_requisition.view_purchase_requisition_form')
        context = {
            "default_purchase_request_id": self.id,
            'default_seq': self.name,
            'default_requester_id': self.requester_id.id,
            'default_department_id': self.department_id.id,
            "default_line_ids": purchase_requisition_line_vals,
        }
        action = {
            'name': _('Create PA'),
            'view_mode': 'form',
            'res_model': 'purchase.requisition',
            'view_id': form_view_id.id,
            'type': 'ir.actions.act_window',
            'context': context,
        }
        return action


class PurchaseRequestLine(models.Model):
    _name = 'purchase.request.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Purchase Request Line'
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', string='Product', required=True, domain=[('type', '=', 'product')])
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True)
    product_default_code = fields.Char(string='Internal Reference', related='product_id.default_code', store=1,
                                       readonly=1)
    product_code = fields.Char(string='Vendor Product Code', readonly=True,
                               help="This vendor's product code will be used when printing a request for quotation. Keep empty to use the internal one.")
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', )
    purchase_request_id = fields.Many2one('purchase.request', string='Request')
    recommendation = fields.Char(string='Recommendation')
    cost = fields.Float(string="", required=False, )
    total_cost = fields.Float(string="", compute='_compute_func_total_cost' )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            line.product_qty = 1
            line.product_uom_id = line.product_id.uom_id
            line.cost = line.product_id.standard_price
            if line.product_id.product_tmpl_id.seller_ids:
                line.product_code = line.product_id.product_tmpl_id.seller_ids[0].product_code

    @api.depends('cost', 'product_qty')
    def _compute_func_total_cost(self):
        for rec in self:
            rec.total_cost = (rec.cost or 0) * (rec.product_qty or 0)
