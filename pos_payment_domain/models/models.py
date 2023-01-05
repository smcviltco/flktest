# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_round


class PosOrderInh(models.Model):
    _inherit = 'pos.order'

    def action_create(self):
        self.action_pos_order_paid()

    def action_pos_order_paid(self):
        self.ensure_one()

        # TODO: add support for mix of cash and non-cash payments when both cash_rounding and only_round_cash_method are True
        if not self.config_id.cash_rounding \
           or self.config_id.only_round_cash_method \
           and not any(p.payment_method_id.is_cash_count for p in self.payment_ids):
            total = self.amount_total
        else:
            total = float_round(self.amount_total, precision_rounding=self.config_id.rounding_method.rounding, rounding_method=self.config_id.rounding_method.rounding_method)
        print(self.amount_paid)
        print(total)
        if not float_is_zero(round(total, 2) - round(self.amount_paid, 2), precision_rounding=self.currency_id.rounding):
            raise UserError(_("Order %s is not fully paid.", self.name))

        self.write({'state': 'paid'})

        return True


class ResPartnerInh(models.Model):
    _inherit = 'res.partner'

    type = fields.Selection(
        [('contact', 'Branch'),
         ('invoice', 'Invoice Address'),
         ('delivery', 'Delivery Address'),
         ('other', 'Other Address'),
         ("private", "Private Address"),
         ], string='Address Type',
        default='contact',
        help="Invoice & Delivery addresses are used in sales orders. Private addresses are only visible by authorized users.")

    def action_view_sale_order(self):
        pass


class PosPaymentInh(models.Model):
    _inherit = 'pos.payment.method'

    receivable_account_id = fields.Many2one('account.account',
                                            string='Intermediary Account',
                                            required=True,
                                            domain=[],
                                            default=lambda
                                                self: self.env.company.account_default_pos_receivable_account_id,
                                            ondelete='restrict',
                                            help='Account used as counterpart of the income account in the accounting entry representing the pos sales.')
