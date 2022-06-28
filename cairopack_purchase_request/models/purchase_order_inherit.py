# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_request_id = fields.Many2one('purchase.request', string='Purchase Request')

    seq = fields.Char(string='PR NO.', )
    requester_id = fields.Many2one('res.users', )
    department_id = fields.Many2one('hr.department', string='Department')
    type_purchase = fields.Selection([('local', 'Local'), ('foreign', 'Foreign')], string="Type")

    def _prepare_picking(self):
        res = super(PurchaseOrder, self)._prepare_picking()
        res.update({
            'type': self.type_purchase
        })
        return res

    def _prepare_invoice(self):
        res = super(PurchaseOrder, self)._prepare_invoice()
        res['type'] = self.type_purchase
        return res

    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        super(PurchaseOrder, self)._onchange_requisition_id()
        if self.requisition_id:
            self.requester_id = self.requisition_id.requester_id.id
            self.department_id = self.requisition_id.department_id.id
            self.purchase_request_id = self.requisition_id.purchase_request_id.id
            self.seq = self.requisition_id.seq




class PurchaseOrderLineInherit(models.Model):
    _inherit = 'purchase.order.line'

    purchase_request_line_id = fields.Many2one(comodel_name="purchase.request.line", string="Purchase Request Line",
                                               required=False, )
    purchase_request_line_ids = fields.Many2many("purchase.request.line", copy=False)
