from odoo import fields, models, api, _



class ResCompany(models.Model):
    _inherit = 'res.company'
    fax = fields.Char(string="Fax")