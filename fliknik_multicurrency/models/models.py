# -*- coding: utf-8 -*-

from odoo import models, fields, api
# -*- coding: utf-8 -*-
from odoo.exceptions import UserError


class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.move_id.is_spot_rate:
            self = self.with_context(override_currency_rate=self.move_id.spot_rate)
        return super(AccountInvoiceLine, self)._onchange_product_id()


class AccountMoveInh(models.Model):
    _inherit = 'account.move'

    is_spot_rate = fields.Boolean('')
    spot_rate = fields.Float()

    def action_post(self):
        """ Creates invoice related analytics and financial move lines """
        if self.is_spot_rate and self.spot_rate == 0:
            raise UserError('Spot rate should be greater than 0.')
        if self.is_spot_rate:
            self = self.with_context(override_currency_rate=self.spot_rate)
        return super(AccountMoveInh, self).action_post()


# class AccountPayment(models.Model):
#     _inherit = 'account.payment'
#
#     is_spot_rate = fields.Boolean()
#     spot_rate = fields.Float()
#
#     def _create_transfer_entry(self, amount):
#         """ Create the journal entry corresponding to the 'incoming money' part of an internal transfer, return the reconciliable move line
#         """
#         if self.is_spot_rate:
#             self = self.with_context(override_currency_rate=self.spot_rate)
#         return super(AccountPayment, self)._create_transfer_entry(amount=amount)
#
#     @api.depends('invoice_ids', 'amount', 'date', 'currency_id','spot_rate')
#     def _compute_payment_difference(self):
#         if self.is_spot_rate:
#             self = self.with_context(override_currency_rate=self.spot_rate)
#         return super(AccountPayment, self)._compute_payment_difference()
#
#     def _create_payment_entry(self, amount):
#         """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
#             Return the journal entry.
#         """
#         if self.is_spot_rate:
#             self = self.with_context(override_currency_rate=self.spot_rate)
#         return super(AccountPayment, self)._create_payment_entry(amount=amount)
#




