
from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    type_sale = fields.Selection([('local','Local'),('foreign','Foreign')],string='Type')

    def _prepare_invoice(self):
        res = super(SaleOrder,self)._prepare_invoice()
        res.update({
            'type': self.type_sale
        })
        return res

    def _action_confirm(self):
        res=super(SaleOrder,self)._action_confirm()
        for rec in self:
            rec.picking_ids.write({'type': rec.type_sale})
        return res



