# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    vendor_ids = fields.Many2many('res.partner', string='Vendors')