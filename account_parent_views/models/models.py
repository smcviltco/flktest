from odoo import api, fields, models


class AccountTypeOthers(models.Model):
    _inherit = "account.account.type"

    type = fields.Selection([
        ('other', 'Regular'),
        ('receivable', 'Receivable'),
        ('payable', 'Payable'),
        ('liquidity', 'Liquidity'),
        ('others', 'Others'),
    ], required=True, default='other',
        help="The 'Internal Type' is used for features available on " \
             "different types of accounts: liquidity type is for cash or bank accounts" \
             ", payable/receivable is for vendor/customer accounts.")
    internal_group = fields.Selection([
        ('equity', 'Equity'),
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('off_balance', 'Off Balance'),
        ('others', 'Others'),
    ], string="Internal Group",
        required=True,
        help="The 'Internal Group' is used to filter accounts based on the internal group set on the account type.")


class AccountParentView(models.Model):
    _inherit = "account.account"

    account = fields.Many2one('account.account',string="Parent Account" ,domain="[('user_type_id','=','View')]")


class AccountMoveTypeView(models.Model):
    _inherit = "account.move.line"

    # account_id = fields.Many2one('account.account', string='Account',
    #                              index=True, ondelete="cascade",
    #                              domain="[('deprecated', '=', False),('company_id', '=', 'company_id'),"
    #                                     "('is_off_balance', '=', False)]",
    #                              check_company=True,
    #                              tracking=True)
    # account_id = fields.Many2one('account.account', string="Account", domain="[('user_type_id','!=','View')]")
    account_id = fields.Many2one('account.account', string="Account")

    account_ids = fields.Many2many('account.account', string='Accounts', compute='_compute_account_ids')

    @api.depends('account_id')
    def _compute_account_ids(self):
        self.account_ids = self.env['account.account'].search([('user_type_id.name', '!=', 'View')])

class PurchaseField(models.Model):
    _inherit = "purchase.order"

    bill_of_entry = fields.Char(string="Bill Of Entry")