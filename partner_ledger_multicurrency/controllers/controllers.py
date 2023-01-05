# -*- coding: utf-8 -*-
# from odoo import http


# class PartnerLedgerMulticurrency(http.Controller):
#     @http.route('/partner_ledger_multicurrency/partner_ledger_multicurrency/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/partner_ledger_multicurrency/partner_ledger_multicurrency/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('partner_ledger_multicurrency.listing', {
#             'root': '/partner_ledger_multicurrency/partner_ledger_multicurrency',
#             'objects': http.request.env['partner_ledger_multicurrency.partner_ledger_multicurrency'].search([]),
#         })

#     @http.route('/partner_ledger_multicurrency/partner_ledger_multicurrency/objects/<model("partner_ledger_multicurrency.partner_ledger_multicurrency"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('partner_ledger_multicurrency.object', {
#             'object': obj
#         })
