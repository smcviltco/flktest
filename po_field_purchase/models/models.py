from odoo import api, fields, models


class PurchaseType(models.Model):
    _inherit = "purchase.order"

    purchase_type = fields.Selection([
        ('local', 'Local'),
        ('import', 'Import'),
    ], string="Purchase Type", required=True)

