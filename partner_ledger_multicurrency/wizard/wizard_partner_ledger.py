from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date

class PartnerLedgerWizard(models.TransientModel):
    _name = 'partner.ledger.multicurrency'
    _description = 'Multi currency ledger'
    
    partner_ids = fields.Many2many('res.partner', string="Partner's")
    date_from =  fields.Date(string='Date From', required=True, default=datetime.today())
    date_to =  fields.Date(string='Date To', required=True, default=datetime.today())
    
    targeted_moves = fields.Selection([
        ('posted_only', 'All posted Entries'),
        ('all', 'All Entries')], string='Targeted Moves', default='all')
    
    currency_ids = fields.Many2many('res.currency', string = 'Currency',required = True)
    partner_account = fields.Many2one('account.account',string="Account" ,required = True)
    initial_bal = fields.Boolean('Show initial Balance')

    def create_partner_report(self):
        data={}
        data['form'] = self.read()[0]
        pt=self.env['account.account'].search([],limit=5)
        obj = []
        obj.append(pt)
        data['acc'] = obj
        data['pt'] = pt
        return self.env.ref('partner_ledger_multicurrency.multicurrency_ledger').report_action(self, data=data)
    
    
    
    