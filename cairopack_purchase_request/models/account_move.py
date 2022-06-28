from odoo import api, fields, models


class account_move(models.Model):
    _inherit = 'account.move'

    type = fields.Selection([('local', 'Local'), ('foreign', 'Foreign')],string="type")
