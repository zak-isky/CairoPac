# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from functools import reduce

class PurchasePlanWizard(models.TransientModel):
    _name = "purchase.plan.wizard"

    partner_id = fields.Many2one('res.partner', string='Vendor')
    purchase_plan_id = fields.Many2one('purchase.plan')
    purchase_plan_line_wizard_ids = fields.One2many('purchase.plan.line.wizard', 'purchase_plan_wizard_id')
    partner_ids = fields.Many2many('res.partner', string='Vendors')

    @api.onchange('purchase_plan_line_wizard_ids','partner_ids')
    def onchange_partner(self):
        partner_lst = []
        intersect_lst = []
        for line in self.purchase_plan_line_wizard_ids:
            partner_lst.append(line.product_id.vendor_ids.ids)
        if partner_lst:
            intersect_lst = list(reduce(set.intersection, [set(item) for item in partner_lst]))
        self.partner_ids = [(6,0, intersect_lst)]

    def action_create_po(self):
        for rec in self:
            greater_done_qty = rec.purchase_plan_line_wizard_ids.filtered(lambda line: line.done_qty > line.product_qty)
            zero_done_qty = rec.purchase_plan_line_wizard_ids.filtered(lambda line: line.done_qty <= 0.0)
            if greater_done_qty:
                raise ValidationError(_('Purchased quantity must not be greater than product qty.'))
            if zero_done_qty:
                raise ValidationError(_('Purchased quantity must be greater than zero.'))
            if len(rec.purchase_plan_line_wizard_ids.ids) > 0:
                purchase_order_line = self.env['purchase.order.line']
                purchase_order = self.env['purchase.order'].create({
                    'partner_id': rec.partner_id.id,
                    'date_order': rec.purchase_plan_id.plan_date,
                    'purchase_plan_id': rec.purchase_plan_id.id,
                })
                for line in rec.purchase_plan_line_wizard_ids:
                    purchase_order_line.create({
                        'order_id': purchase_order.id,
                        'name': line.product_id.name,
                        'product_id': line.product_id.id,
                        'product_uom': line.product_id.uom_id.id,
                        'product_qty': line.done_qty,
                        'price_unit': line.product_id.standard_price,
                        'date_planned': rec.purchase_plan_id.plan_date,
                    })
                    line.purchase_plan_line_id.done_qty += line.done_qty

                total_diff_lines = sum(line.product_qty - line.done_qty for line in rec.purchase_plan_id.purchase_plan_line_ids)
                if total_diff_lines == 0:
                    rec.purchase_plan_id.state = 'done'
                for line in rec.purchase_plan_id.purchase_plan_line_ids:
                    line.select_po = False
            else:
                raise ValidationError(_('Purchase lines must not be empty'))


class PurchasePlanLineWizard(models.TransientModel):
    _name = "purchase.plan.line.wizard"

    product_id = fields.Many2one('product.product')
    product_qty = fields.Integer(string="Quantity")
    done_qty = fields.Integer(string="Purchased Quantity")
    purchase_plan_wizard_id = fields.Many2one('purchase.plan.wizard')
    purchase_plan_line_id = fields.Many2one('purchase.plan.line')
    qty_available = fields.Float(related='product_id.qty_available')