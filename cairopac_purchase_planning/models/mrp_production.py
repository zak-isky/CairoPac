from odoo import models, fields, api, exceptions
from datetime import datetime


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    purchase_plan_id = fields.Many2one(comodel_name="purchase.plan", string="", required=False, )

