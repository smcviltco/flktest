from odoo import api, fields, models


class ResInherit(models.Model):
    _inherit = "res.partner"

    itf_263 = fields.Selection([('register', 'Register'), ('unregister', 'UnRegister')], default='unregister')
    itf_265 = fields.Char(string='ITF @265' )
    date_valid_from = fields.Date(string='Date Valid From')
    date_valid_to = fields.Date(string='Date Valid To')

    bp = fields.Selection([('register', 'Register'), ('unregister', 'UnRegister')], default='unregister')

