# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from functools import reduce

READONLY_STATES = {
    'purchase': [('readonly', True)],
    'done': [('readonly', True)],
    'cancel': [('readonly', True)],
}


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_plan_id = fields.Many2one('purchase.plan')
    partner_ids = fields.Many2many('res.partner', string='Vendors')
    product_ids = fields.Many2many('product.product', string='Products')
    partner_id = fields.Many2one('res.partner', string='Vendor',
                                 required=True, states=READONLY_STATES,
                                 change_default=True, tracking=True,
                                 domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                 help="You can find a vendor by its Name, TIN, Email or Internal Reference.")

    # partner_id = fields.Many2one('res.partner', string='Vendor',
    #                              required=True, states=READONLY_STATES,
    #                              change_default=True, tracking=True,
    #                              domain="['|', ('company_id', '=', False), ('company_id', '=', company_id),('id','in',partner_ids)]",
    #                              help="You can find a vendor by its Name, TIN, Email or Internal Reference.")

    @api.onchange('order_line', 'partner_ids')
    def onchange_partner(self):
        partner_lst = []
        intersect_lst = []
        for line in self.order_line:
            partner_lst.append(line.product_id.vendor_ids.ids)
        if partner_lst:
            intersect_lst = list(reduce(set.intersection, [set(item) for item in partner_lst]))
        self.partner_ids = [(6, 0, intersect_lst)]

    @api.onchange('partner_id')
    def get_all_product(self):
        for rec in self:
            if rec.partner_id:
                all_product = self.env['product.product'].search([('vendor_ids', '=', rec.partner_id.id)])
                product_lst = []
                for product in all_product:
                    product_lst.append(product.id)
                self.product_ids = [(6, 0, product_lst)]


class PurchasePlan(models.Model):
    _name = 'purchase.plan'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char()
    plan_date = fields.Date(string="Plan Date", default=fields.Date.context_today)
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    plan_type = fields.Selection([('manufacture', 'Manufacturing'), ('direct', 'Direct Plan')], string="Plan Type")
    manufacturing_plan_line_ids = fields.One2many('manufacturing.plan.line', 'purchase_plan_id',
                                                  string="Manufacturing_Plan Lines", copy=True)
    purchase_plan_line_ids = fields.One2many('purchase.plan.line', 'purchase_plan_id', string="Purchase Lines",
                                             copy=True)
    purchase_count = fields.Integer(compute='get_purchase_count', store=1)
    purchase_ids = fields.One2many('purchase.order', 'purchase_plan_id', string="Purchase Orders")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('approve', 'Approved'),
        ('done', 'Done'),
        ('close', 'Closed')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    mrp_count = fields.Integer(compute='get_mrp_count', store=1)
    mrp_ids = fields.One2many('mrp.production', 'purchase_plan_id', string="Manufacture Orders")
    sales_forcasting_id = fields.Many2one('sales.forcasting', string='Sales Forcasting')

    @api.onchange('sales_forcasting_id')
    def onchange_sales_forcasting(self):
        for rec in self:
            if rec.sales_forcasting_id:
                line_product = rec.sales_forcasting_id.forcasting_lines.mapped('product_id')
                for product in line_product:
                    rec.manufacturing_plan_line_ids = [(0, 0, {
                        'product_id': product.id,
                        'product_qty': sum([l.product_qty for l in rec.sales_forcasting_id.forcasting_lines.filtered(
                            lambda p: p.product_id.id == product.id)]),
                    })]
            else:
                rec.manufacturing_plan_line_ids = False

    @api.onchange('plan_type')
    def onchange_plan_type(self):
        for rec in self:
            if rec.plan_type == 'direct':
                rec.manufacturing_plan_line_ids = False

    @api.depends('purchase_ids')
    def get_purchase_count(self):
        for rec in self:
            rec.purchase_count = len(rec.purchase_ids.ids)

    @api.depends('mrp_ids')
    def get_mrp_count(self):
        for rec in self:
            rec.mrp_count = len(rec.mrp_ids.ids)

    @api.constrains('date_from', 'date_to')
    def constrain_dates(self):
        for rec in self:
            if rec.date_from > rec.date_to:
                raise ValidationError(_('Date to must be greater than date from.'))

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('purchase.plan') or '/'
        return super(PurchasePlan, self).create(vals)

    def button_submit(self):
        for rec in self:
            rec.state = 'submit'

    def button_approve(self):
        for rec in self:
            rec.state = 'approve'

    def button_close(self):
        for rec in self:
            rec.state = 'close'

    def action_view_purchase(self):
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        action['domain'] = [('id', 'in', self.purchase_ids.ids)]
        return action

    def action_view_mrp(self):
        action = self.env.ref('mrp.mrp_production_action').read()[0]
        action['domain'] = [('id', 'in', self.mrp_ids.ids)]
        return action

    def action_create_po(self):
        purchase_plan_wizard = self.env['purchase.plan.wizard']
        purchase_plan_line_wizard = self.env['purchase.plan.line.wizard']
        purchase_plan = purchase_plan_wizard.create({
            'purchase_plan_id': self.id,
        })
        partners = []
        for line in self.purchase_plan_line_ids:
            if not line.create_po and line.select_po:
                purchase_plan_line_wizard.create({
                    'purchase_plan_wizard_id': purchase_plan.id,
                    'product_id': line.product_id.id,
                    'product_qty': line.product_qty - line.done_qty,
                    'done_qty': ((line.product_qty - line.done_qty) - line.qty_available) if ((
                                                                                                      line.product_qty - line.done_qty) - line.qty_available) > 0.0 else 0.0,
                    'purchase_plan_line_id': line.id,
                })
                partners.append(line.product_id.vendor_ids.ids)
        if partners:
            partner_lst = list(reduce(set.intersection, [set(item) for item in partners]))
            purchase_plan.partner_ids = partner_lst

        view_id = self.env.ref('cairopac_purchase_planning.purchase_plan_wizard_form_view').id
        return {
            'name': _('Purchase Plan'),
            'view_mode': 'form',
            'res_model': 'purchase.plan.wizard',
            'view_id': view_id,
            'res_id': purchase_plan.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.onchange('manufacturing_plan_line_ids')
    def onchange_manufacturing_lines(self):
        def _check_lines(check_lines, product_id):
            for idx, l in enumerate(check_lines):
                if product_id == l[2]['product_id']:
                    return idx
            return False

        for rec in self:
            if rec.plan_type == 'manufacture':
                rec.purchase_plan_line_ids = [(6, 0, [])]
                lines = []
                for line in rec.manufacturing_plan_line_ids:
                    if line.product_id.bom_ids:
                        for bom_component_line in line.product_id.bom_ids[0].bom_line_ids:
                            line_idx = _check_lines(lines, bom_component_line.product_id.id)
                            if line_idx is not False:
                                lines[line_idx][2]['product_qty'] += bom_component_line.product_qty * line.product_qty
                            else:
                                lines.append((0, 0, {'product_id': bom_component_line.product_id.id,
                                                     'product_qty': bom_component_line.product_qty * line.product_qty}))
                rec.purchase_plan_line_ids = lines


class ManufacturingPlanLine(models.Model):
    _name = 'manufacturing.plan.line'

    product_id = fields.Many2one('product.product')
    product_qty = fields.Integer(string="Quantity")
    purchase_plan_id = fields.Many2one('purchase.plan', index=True, required=True, ondelete='cascade')
    state = fields.Selection(related='purchase_plan_id.state', store=True, readonly=False)

    def action_create_mo(self):
        mrp_order = self.env['mrp.production'].create(
            {'product_id': self.product_id.id, 'product_qty': self.product_qty,
             'purchase_plan_id': self.purchase_plan_id.id,
             'product_uom_id': self.product_id.uom_id.id})
        mrp_order._onchange_product_id()
        mrp_order._onchange_product_qty()
        mrp_order._onchange_bom_id()
        mrp_order._onchange_move_raw()
        mrp_order.write({'product_qty': self.product_qty})
        mrp_order._onchange_product_qty()
        mrp_order._onchange_move_raw()

        view_id = self.env.ref('mrp.mrp_production_form_view').id
        return {
            'name': _('Manufacture Order'),
            'view_mode': 'form',
            'res_model': 'mrp.production',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_id': mrp_order.id
        }


class PurchasePlanLine(models.Model):
    _name = 'purchase.plan.line'

    product_id = fields.Many2one('product.product', required=1)
    product_qty = fields.Integer(string="Quantity")
    done_qty = fields.Integer(string="Purchased Quantity", copy=False)
    purchase_plan_id = fields.Many2one('purchase.plan', index=True, required=True, ondelete='cascade')
    create_po = fields.Boolean(string="Create PO", compute="check_qty", copy=False)
    state = fields.Selection(related='purchase_plan_id.state', store=True, readonly=False)
    select_po = fields.Boolean("Select", copy=False)
    qty_available = fields.Float(related='product_id.qty_available')

    def unlink(self):
        for rec in self:
            if rec.state in ['approve', 'done']:
                raise ValidationError("You cannot delete validated lines.")
            else:
                return super(PurchasePlanLine, self).unlink()

    @api.depends('product_qty', 'done_qty')
    def check_qty(self):
        for rec in self:
            rec.create_po = False
            if rec.done_qty == rec.product_qty:
                rec.create_po = True

    def action_create_po(self):
        purchase_plan_wizard = self.env['purchase.plan.wizard']
        purchase_plan_line_wizard = self.env['purchase.plan.line.wizard']
        purchase_plan = purchase_plan_wizard.create({
            'purchase_plan_id': self.purchase_plan_id.id,
            'partner_ids': self.product_id.vendor_ids.ids,
        })
        if not self.create_po:
            purchase_plan_line_wizard.create({
                'purchase_plan_wizard_id': purchase_plan.id,
                'product_id': self.product_id.id,
                'product_qty': (self.product_qty - self.done_qty),
                'done_qty': ((self.product_qty - self.done_qty) - self.qty_available) if ((
                                                                                                  self.product_qty - self.done_qty) - self.qty_available) > 0.0 else 0.0,
                'purchase_plan_line_id': self.id,
            })
        view_id = self.env.ref('cairopac_purchase_planning.purchase_plan_wizard_form_view').id
        return {
            'name': _('Purchase Plan'),
            'view_mode': 'form',
            'res_model': 'purchase.plan.wizard',
            'view_id': view_id,
            'res_id': purchase_plan.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
