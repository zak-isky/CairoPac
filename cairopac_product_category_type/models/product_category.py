from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'
    
    type = fields.Selection(
        string='Type',
        selection=[('raw', 'Raw Material'), ('finish', 'Finish Product'),
                   ('spare', 'Spare Parts'), ('progress', 'Work In Progress')])
