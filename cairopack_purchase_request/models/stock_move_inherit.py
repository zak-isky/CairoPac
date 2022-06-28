# -*- coding: utf-8 -*-
from odoo import fields, models, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id, description):
        result = super(StockMove, self)._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id,
                                                                   description)
        for move in self:
            if move.picking_id.analytic_account_id:
                for num in range(0, 2):
                    # Add analytic account in debit line
                    if result[num][2]['debit'] > 0.0:
                        result[num][2]['analytic_account_id'] = move.picking_id.analytic_account_id.id
        return result
