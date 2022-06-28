from odoo import fields, models, api


class SalesForcasting(models.Model):
    _name = 'sales.forcasting'

    name = fields.Char(string="Sequence", readonly=True, required=True, copy=False, default='/')
    partner_id = fields.Many2many('res.partner', string='Customer')
    date = fields.Date(string='Date')
    forcasting_lines = fields.One2many('sales.forcasting.line', 'forcasting_id', string='Lines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm')
    ], default='draft')

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'sales.forcasting') or '/'
        result = super(SalesForcasting, self).create(vals)
        return result

    def set_to_confirm(self):
        for rec in self:
            rec.state = 'confirm'
            rec.forcasting_lines.filtered(lambda line: line.product_qty <= 0).unlink()

    @api.onchange('partner_id')
    def on_change_customer(self):
        for rec in self:
            if rec.partner_id:
                customers = self.env['res.partner'].search([('id', 'in', rec.partner_id.ids)])
                lines_to_remove = rec.forcasting_lines.filtered(
                    lambda
                        line: line.partner_ids.id not in customers.ids)
                rec.forcasting_lines = [(2, line.id) for line in lines_to_remove]
                for customer in customers:
                    domain = [('sale_ok', '=', True)]
                    products = self.env['product.product'].search_read(domain)
                    if customer.id not in [
                        l.partner_ids.id for l in rec.forcasting_lines]:
                        for p in products:
                            rec.forcasting_lines = [(0, 0, {
                                'product_id': p['id'],
                                'partner_ids': customer.id
                            })]
            else:
                rec.forcasting_lines = [(5, 0, 0)]


class SalesForcastingLine(models.Model):
    _name = 'sales.forcasting.line'

    product_id = fields.Many2one('product.product', string='Products', required=True)
    product_qty = fields.Float(string='Quantity', required=True)
    forcasting_id = fields.Many2one('sales.forcasting', string='Sales Forcasting')
    partner_ids = fields.Many2one('res.partner', string='Customers')
    date = fields.Date(related='forcasting_id.date',string='Date',store=True)
