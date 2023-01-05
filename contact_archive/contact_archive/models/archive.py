from odoo import api, fields, models

class ResInherit(models.Model):
    _inherit = "res.partner"

    active = fields.Boolean('Active', default=True)


    def action_approve(self):
        self.active = True

    @api.model
    def create(self,vals):
        record = super(ResInherit,self).create(vals)
        record.active = False
        return record


