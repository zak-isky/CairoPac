# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_parent_product = fields.Boolean(string='Parent Product')
    product_item_ids = fields.One2many('product.item', 'product_tmpl_id', string='Items')

    def name_get(self):
        new_format = []
        for rec in self:
            new_info = " "
            new_info += rec.name or " "
            new_format.append((rec.id, new_info))
        return new_format


class ProductItem(models.Model):
    _name = 'product.item'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Product Item'
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', string='Product', required=True, domain=[('type', '=', 'product')])
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True)
    product_tmpl_id = fields.Many2one('product.template', string="Product Template", ondelete='cascade', required=True,
                                      index=True)

    parent_product_items = fields.Char(string='Items', compute='_get_product_items')

    @api.depends('product_id')
    def _get_product_items(self):
        for item in self:
            item.parent_product_items = ', '.join(
                product.display_name for product in
                item.product_id.product_tmpl_id.product_item_ids.mapped('product_id'))


class Product(models.Model):
    _inherit = 'product.product'
    _order = 'id, default_code, name'

    def name_get(self):
        new_format = []
        for rec in self:
            new_info = " "
            new_info += rec.name or " "
            new_format.append((rec.id, new_info))
        return new_format
