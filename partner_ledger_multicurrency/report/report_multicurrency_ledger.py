from odoo import models, fields, api, _
from datetime import datetime, timedelta, date, time
from dateutil.rrule import rrule, MONTHLY
from dateutil.relativedelta import relativedelta
from collections import OrderedDict
# import pandas as pd
import calendar
import sys


class MulticurrencyPartnerLedgerReport(models.AbstractModel):
    _name = 'report.partner_ledger_multicurrency.multicurrencyledger_report'

    #     @api.model_create_multi
    #     def str_to_class(classname):
    #         return getattr(sys.modules[__name__], classname)

    def action_create_messages(self, rec, qty):
        users = self.env['res.users'].search([])
        a = self.env['res.users'].search([('login', '=', 'info@mantechpk.com')])
        subtype = self.env['mail.message.subtype'].search([('name', '=', 'Discussions')])
        author_id = self.env['res.users'].sudo().browse(a.id).partner_id.id
        for r in users:
            if r.has_group('jointnutre_reordering.group_inventory_manager'):
                mail_channel = self.env["mail.channel"].sudo().search([('name', '=', r.name + ', ' + a.name)], limit=1)
                # if not mail_channel:
                #     line_val = []
                #     line_val.append([(0, 0, {
                #         'partner_id': a.partner_id.id,
                #         'partner_email': a.partner_id.email,
                #     })])
                #     line_val.append([(0, 0, {
                #         'partner_id': r.partner_id.id,
                #         'partner_email': r.partner_id.email,
                #     })])
                #     print(line_val)
                #     mail_channel = self.env['mail.channel'].create({
                #         'name': r.name + ', ' + a.name,
                #         'channel_last_seen_partner_ids': line_val,
                #         'public': 'private',
                #         'channel_type': 'chat',
                #         'email_send': False,
                #     })
                body = 'Product [' + rec.name + '] has reached its minimum quantity.And its current stock is ' + qty
                if mail_channel:
                    message = mail_channel.sudo().with_context(mail_create_nosubscribe=True).message_post(
                        author_id=author_id,
                        email_from=False,
                        res_id=mail_channel.id,
                        model='mail.channel',
                        partner_ids=[
                            r.partner_id.id],
                        channel_ids=[],
                        body=body,
                        message_type='comment',
                        subtype_id=subtype.id)
                    return message and message.id or False

    def initial_balance(self, date_from):
        pass

    def get_currecy_rate(self, date, currency):
        rate_list = self.env['res.currency.rate'].search([('currency_id', '=', currency.id), ('name', '<=', date)])
        sorted_rate_list = rate_list.sorted(key='name')
        latest_rate = sorted_rate_list[-1].rate
        return latest_rate

    def get_partner_records(self, partner, crncy, date_from, date_to, account_id, state):
        if state == 'posted_only':

            records = self.env['account.move.line'].search([('partner_id', '=', partner.id),
                                                            ('currency_id', '=', crncy.id),
                                                            ('date', '>=', date_from),
                                                            ('date', '<=', date_to),
                                                            ('account_id', '=', account_id.id),
                                                            ('parent_state', '=', 'posted')])

        else:
            records = self.env['account.move.line'].search([('partner_id', '=', partner.id),
                                                            ('currency_id', '=', crncy.id),
                                                            ('date', '>=', date_from),
                                                            ('date', '<=', date_to),
                                                            ('account_id', '=', account_id.id)])
        return records

    def partner_journal_item(self, partnerss, jv, crncy, comp_currency, date_to, account_id):
        v_dict = {}

        bal = jv.debit - jv.credit

        v_dict = {
            'prtnr': partnerss,
            'currency': crncy,
            'date': jv.date,
            'ref': jv.name,
            'account': account_id.code,
            'debit': jv.debit,
            'credit': jv.credit,
            'balance': bal,
            'o_debit': 0.0,
            'o_credit': 0.0,
            'o_bal': 0.0,
            'base_currency': comp_currency
        }

        if jv.currency_id != comp_currency:
            convert_rate = self.get_currecy_rate(date_to, jv.currency_id)
            #             amount = convert_rate * jv.amount_currency
            amount = jv.amount_currency
            if jv.debit > 0.0:
                o_debit = amount
                o_credit = 0.0
                o_bal = amount
                v_dict['o_debit'] = o_debit
                v_dict['o_credit'] = o_credit
                #                 v_dict['o_bal'] = o_bal
                v_dict['o_bal'] = v_dict['o_debit'] - v_dict['o_credit']

            elif jv.credit > 0.0:
                o_debit = 0.0
                o_credit = (amount)
                o_bal = -1 * (amount)
                v_dict['o_debit'] = o_debit
                v_dict['o_credit'] = o_credit
                #                 v_dict['o_bal'] = o_bal
                v_dict['o_bal'] = v_dict['o_debit'] - v_dict['o_credit']

        return v_dict

    def partner_currency_initial_bal(self, partner_id, curncy, date_from, account_id, company_currency):
        recs = self.env['account.move.line'].search([('partner_id', '=', partner_id.id),
                                                     ('currency_id', '=', curncy.id),
                                                     ('date', '<', date_from),
                                                     ('account_id', '=', account_id.id),
                                                     ('parent_state', '=', 'posted')])

        debit = 0.0
        credit = 0.0
        balance = 0.0
        if curncy == company_currency:
            for a in recs:
                debit = debit + a.debit
                credit = credit + a.credit

            balance = debit - credit
            balance = "{:.2f}".format(balance)
            return balance
        else:
            for b in recs:
                if b.amount_currency < 0:

                    debit = debit + 0.0
                    credit = credit + b.amount_currency
                else:
                    debit = debit + b.amount_currency
                    credit = credit + 0.0

            balance = debit - credit
            balance = "{:.2f}".format(balance)
            return float(balance)

    def get_opening_bal(self, partner, data):
        open_bal = self.env['account.move.line'].search(
            [('partner_id', '=', partner.id), ('date', '<', data['form']['date_from']),
             ('move_id.state', '=', 'posted'), ('full_reconcile_id', '=', False), ('balance', '!=', 0),
             ('account_id.reconcile', '=', True), ('full_reconcile_id', '=', False), '|',
             ('account_id.internal_type', '=', 'payable'), ('account_id.internal_type', '=', 'receivable')])
        bal = 0
        for rec in open_bal:
            bal = bal + rec.balance
        print(bal)
        return bal

    @api.model
    def _get_report_values(self, docids, data=None):

        date_from = data['form']['date_from']
        date_to = data['form']['date_to']

        initial_check = data['form']['initial_bal']

        if data['form']['partner_ids']:
            partner_rec = self.env['res.partner'].search([('id', 'in', data['form']['partner_ids'])])
        elif not data['form']['partner_ids']:
            partner_rec = self.env['res.partner'].search([])

        account_id = self.env['account.account'].search([('id', '=', data['form']['partner_account'][0])])
        currencies = self.env['res.currency'].search([('id', 'in', data['form']['currency_ids'])])
        comp_currency = self.env.company.currency_id
        state = data['form']['targeted_moves']

        vals = []
        vals1 = []
        partner_total = []
        initial_bal_list = []

        for partnerss in partner_rec:
            total_val = {}

            partner_total_debit = 0.0
            partner_total_credit = 0.0
            partner_total_balance = 0.0

            partner_total_othdebit = 0.0
            partner_total_othcredit = 0.0
            partner_total_othbalance = 0.0

            total_val['partner'] = partnerss

            for crncy in currencies:
                if initial_check == True:
                    ibal = {}
                    initial_bal = self.partner_currency_initial_bal(partnerss, crncy, date_from, account_id,
                                                                    comp_currency)
                    ibal = {'partner': partnerss,
                            'currency': crncy,
                            'init_bal': initial_bal}

                    initial_bal_list.append(ibal)

                recs = self.get_partner_records(partnerss, crncy, date_from, date_to, account_id, state)

                for jv in recs:
                    jv_dict = self.partner_journal_item(partnerss, jv, crncy, comp_currency, date_to, account_id)
                    vals.append(jv_dict)

                    partner_total_debit = partner_total_debit + jv_dict['debit']
                    partner_total_credit = partner_total_credit + jv_dict['credit']
                    partner_total_balance = partner_total_balance + jv_dict['balance']

                    partner_total_othdebit = partner_total_othdebit + jv_dict['o_debit']
                    partner_total_othcredit = partner_total_othcredit + jv_dict['o_credit']
                    partner_total_othbalance = partner_total_othbalance + jv_dict['o_bal']

            total_val['debit'] = round(partner_total_debit, 2)
            total_val['credit'] = round(partner_total_credit, 2)
            total_val['balance'] = round(partner_total_balance, 2)
            total_val['o_debit'] = round(partner_total_othdebit, 2)
            total_val['o_credit'] = round(partner_total_othcredit, 2)
            total_val['o_bal'] = round(partner_total_othbalance, 2)
            partner_total.append(total_val)
        # print(partner_total)
        # print(initial_bal_list)
        # sale_obj=self.env['sale.order'].search([])[0]
        # subtype_id = self.env['mail.message.subtype'].search([('name','=','Discussions')])
        #         message_obj = self.env['mail.message'].create({  'subject': 'django framework',
        #                         'body': f'comment message from backend python',
        #                         # 'attachment_ids': [[6, 0, self.attatchments_whatsap.ids]],
        #                          'model': 'mail.channel',
        #                         'record_name':'django email task',
        #                         'res_id': self.env['mail.channel'].search([],limit=1).id,
        #                         'message_type':'comment',
        #                         'subtype_id':subtype_id.id,
        #                         'channel_ids':[self.env['mail.channel'].search([],limit=1).id]
        # #                         'no_auto_thread': True,
        # #                         'add_sign': True,
        #                         })
        #         print(message_obj.id)
        #         sale_obj.message_post(body='This is test message from python to odoo')

        return {
            'doc_ids': docids,
            'doc_model': 'account.payment',
            'data': data,
            'partners': partner_rec,
            'currencies': currencies,
            'move_lines': vals,
            'total': partner_total,
            'init_bal': initial_bal_list,
            'company_currency': comp_currency,
            'opening_bal': self.get_opening_bal
        }
