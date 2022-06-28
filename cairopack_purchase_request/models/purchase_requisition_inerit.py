# -*- coding: utf-8 -*-
from odoo import fields, models, _


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    purchase_request_id = fields.Many2one('purchase.request', string='Purchase Request')

    seq = fields.Char(string='PR NO.', readonly=True)
    requester_id = fields.Many2one('res.users', readonly=True)
    department_id = fields.Many2one('hr.department', string='Department', readonly=True)
