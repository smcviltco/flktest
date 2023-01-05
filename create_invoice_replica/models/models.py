# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveInh(models.Model):
    _inherit = 'account.move'

    invoice_types = fields.Selection([('usd', 'USD'), ('zwl', 'ZWL'), ('unofficial', 'Unofficial')], string='Invoice Type')

    def action_account_move_wizard(self):
        selected_ids = self.env.context.get('active_ids', [])
        selected_records = self.env['account.move'].browse(selected_ids)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Invoices',
            'view_id': self.env.ref('create_invoice_replica.view_create_invoice_wizard_form', False).id,
            'target': 'new',
            'context': {'default_move_ids': selected_records.ids},
            'res_model': 'create.invoice.wizard',
            'view_mode': 'form',
        }


class SaleOrderInh(models.Model):
    _inherit = 'sale.order'

    def action_sale_wizard(self):
        selected_ids = self.env.context.get('active_ids', [])
        selected_records = self.env['account.move'].browse(selected_ids)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Sales',
            'view_id': self.env.ref('create_invoice_replica.view_create_sale_wizard_form', False).id,
            'target': 'new',
            'context': {'default_sale_ids': selected_records.ids},
            'res_model': 'create.sale.wizard',
            'view_mode': 'form',
        }


class PurchaseOrderInh(models.Model):
    _inherit = 'purchase.order'

    def action_purchase_wizard(self):
        selected_ids = self.env.context.get('active_ids', [])
        selected_records = self.env['account.move'].browse(selected_ids)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Purchase',
            'view_id': self.env.ref('create_invoice_replica.view_create_purchase_wizard_form', False).id,
            'target': 'new',
            'context': {'default_purchase_ids': selected_records.ids},
            'res_model': 'create.purchase.wizard',
            'view_mode': 'form'
        }


class AccountPaymentInh(models.Model):
    _inherit = 'account.payment'

    def action_payment_wizard(self):
        selected_ids = self.env.context.get('active_ids', [])
        selected_records = self.env['account.move'].browse(selected_ids)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Purchase',
            'view_id': self.env.ref('create_invoice_replica.view_create_payment_wizard_form', False).id,
            'target': 'new',
            'context': {'default_payment_ids': selected_records.ids},
            'res_model': 'create.payment.wizard',
            'view_mode': 'form',
        }
