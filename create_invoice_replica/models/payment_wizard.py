from odoo import models, fields, api


class CreatePaymentWizard(models.TransientModel):
    _name = 'create.payment.wizard'

    company_id = fields.Many2one('res.company')
    payment_ids = fields.Many2many('account.payment')

    def create_data(self):
        for rec in self.payment_ids:
            line_vals = []
            currency = self.env['res.currency'].sudo().search([('name', '=', rec.currency_id.name)])

            partner = self.env['res.partner'].sudo().search([('name', '=', rec.partner_id.name), ('company_id', '=', self.company_id.id)])
            if not partner:
                partner = rec.partner_id.sudo().copy({
                    'name': rec.partner_id.name,
                    'company_id': self.company_id.id
                })
            user = self.env['res.users'].sudo().search([('name', '=', rec.user_id.name)])
            vals = {
                'partner_id': partner.id,
                # 'journal_id': journal.id,
                'currency_id': currency.id,
                # 'date_order': rec.date_order,
                'payment_type': rec.payment_type,
                'partner_type': rec.partner_type,
                'state': 'draft',
                'company_id': self.company_id.id,
                'user_id': user.id,
                'date': rec.date,
                'amount': rec.amount,
                # 'destination_account_id': rec.destination_account_id.id,
                # 'team_id': rec.team_id.id,
            }
            payment = self.env['account.payment'].sudo().with_context(default_company_id=self.company_id.id).create(vals)
            # move.action_post()
