# -*- coding: utf-8 -*-
from odoo import fields, models, _, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # material_request_id = fields.Many2one('material.request', string='Material Request', readonly=1,
    #                                       track_visibility='onchange')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',
                                          track_visibility='onchange')
    type = fields.Selection([('local','Local'),('foreign','Foreign')],string="type")







