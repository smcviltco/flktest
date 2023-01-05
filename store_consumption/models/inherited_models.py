from odoo import api, fields, models, _


class StockLocationInherit(models.Model):
    _inherit = "stock.location"

    is_store_location = fields.Boolean('Is Store Location')
    is_consumption_location = fields.Boolean('Is Consumption Location')


class AccountInherit(models.Model):
    _inherit = "account.account"

    is_stock_account = fields.Boolean('Is Stock Account')
    cgs_account = fields.Boolean('CGS Account')


class AccountJournalInherit(models.Model):
    _inherit = "account.journal"

    is_stock_journal = fields.Boolean('Is Stock Journal')
