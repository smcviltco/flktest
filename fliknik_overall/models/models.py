# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import datetime
from itertools import groupby
from operator import itemgetter
from re import findall as regex_findall
from re import split as regex_split

from dateutil import relativedelta

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_is_zero, float_repr, float_round
from odoo.tools.misc import format_date, OrderedSet
from odoo.exceptions import AccessError, UserError


class PosSessionInh(models.Model):
    _inherit = 'pos.session'

    def action_pos_session_closing_control(self):
        res = super(PosSessionInh, self).action_pos_session_closing_control()
        self.action_update_entry()
        return res

    def action_update_entry(self):
        for order in self.order_ids:
            if self.env.ref('base.main_company').currency_id.id != order.pricelist_id.currency_id.id:
                for move in order.session_move_id:
                    move.button_draft()
                    for line in move.line_ids:
                        line.update({
                            'amount_currency': line.amount_currency*order.pricelist_id.currency_id.rate,
                            'currency_id': order.pricelist_id.currency_id.id,
                        })
                order.session_move_id.button_approved()



    # def _accumulate_amounts(self, data):
    #     # Accumulate the amounts for each accounting lines group
    #     # Each dict maps `key` -> `amounts`, where `key` is the group key.
    #     # E.g. `combine_receivables` is derived from pos.payment records
    #     # in the self.order_ids with group key of the `payment_method_id`
    #     # field of the pos.payment record.
    #     amounts = lambda: {'amount': 0.0, 'amount_converted': 0.0}
    #     tax_amounts = lambda: {'amount': 0.0, 'amount_converted': 0.0, 'base_amount': 0.0, 'base_amount_converted': 0.0}
    #     split_receivables = defaultdict(amounts)
    #     split_receivables_cash = defaultdict(amounts)
    #     combine_receivables = defaultdict(amounts)
    #     combine_receivables_cash = defaultdict(amounts)
    #     invoice_receivables = defaultdict(amounts)
    #     sales = defaultdict(amounts)
    #     taxes = defaultdict(tax_amounts)
    #     stock_expense = defaultdict(amounts)
    #     stock_return = defaultdict(amounts)
    #     stock_output = defaultdict(amounts)
    #     rounding_difference = {'amount': 0.0, 'amount_converted': 0.0}
    #     # Track the receivable lines of the invoiced orders' account moves for reconciliation
    #     # These receivable lines are reconciled to the corresponding invoice receivable lines
    #     # of this session's move_id.
    #     order_account_move_receivable_lines = defaultdict(lambda: self.env['account.move.line'])
    #     rounded_globally = self.company_id.tax_calculation_rounding_method == 'round_globally'
    #     for order in self.order_ids:
    #         # Combine pos receivable lines
    #         # Separate cash payments for cash reconciliation later.
    #         for payment in order.payment_ids:
    #             if self.env.ref('base.main_company').currency_id.id == payment.currency.id:
    #                 amount, date = payment.amount, payment.payment_date
    #             else:
    #                 amount, date = payment.amount_currency, payment.payment_date
    #             if payment.payment_method_id.split_transactions:
    #                 if payment.payment_method_id.is_cash_count:
    #                     split_receivables_cash[payment] = self._update_amounts(split_receivables_cash[payment], {'amount': amount}, date)
    #                 else:
    #                     split_receivables[payment] = self._update_amounts(split_receivables[payment], {'amount': amount}, date)
    #             else:
    #                 key = payment.payment_method_id
    #                 if payment.payment_method_id.is_cash_count:
    #                     combine_receivables_cash[key] = self._update_amounts(combine_receivables_cash[key], {'amount': amount}, date)
    #                 else:
    #                     combine_receivables[key] = self._update_amounts(combine_receivables[key], {'amount': amount}, date)
    #
    #         if order.is_invoiced:
    #             # Combine invoice receivable lines
    #             key = order.partner_id
    #             if self.config_id.cash_rounding:
    #                 invoice_receivables[key] = self._update_amounts(invoice_receivables[key], {'amount': order.amount_paid}, order.date_order)
    #             else:
    #                 invoice_receivables[key] = self._update_amounts(invoice_receivables[key], {'amount': order.amount_total}, order.date_order)
    #             # side loop to gather receivable lines by account for reconciliation
    #             for move_line in order.account_move.line_ids.filtered(lambda aml: aml.account_id.internal_type == 'receivable' and not aml.reconciled):
    #                 order_account_move_receivable_lines[move_line.account_id.id] |= move_line
    #         else:
    #             order_taxes = defaultdict(tax_amounts)
    #             for order_line in order.lines:
    #                 line = self._prepare_line(order_line)
    #                 # Combine sales/refund lines
    #                 sale_key = (
    #                     # account
    #                     line['income_account_id'],
    #                     # sign
    #                     -1 if line['amount'] < 0 else 1,
    #                     # for taxes
    #                     tuple((tax['id'], tax['account_id'], tax['tax_repartition_line_id']) for tax in line['taxes']),
    #                     line['base_tags'],
    #                 )
    #                 sales[sale_key] = self._update_amounts(sales[sale_key], {'amount': line['amount']}, line['date_order'])
    #                 # Combine tax lines
    #                 for tax in line['taxes']:
    #                     tax_key = (tax['account_id'], tax['tax_repartition_line_id'], tax['id'], tuple(tax['tag_ids']))
    #                     order_taxes[tax_key] = self._update_amounts(
    #                         order_taxes[tax_key],
    #                         {'amount': tax['amount'], 'base_amount': tax['base']},
    #                         tax['date_order'],
    #                         round=not rounded_globally
    #                     )
    #             for tax_key, amounts in order_taxes.items():
    #                 if rounded_globally:
    #                     amounts = self._round_amounts(amounts)
    #                 for amount_key, amount in amounts.items():
    #                     taxes[tax_key][amount_key] += amount
    #
    #             if self.company_id.anglo_saxon_accounting and order.picking_ids.ids:
    #                 # Combine stock lines
    #                 stock_moves = self.env['stock.move'].sudo().search([
    #                     ('picking_id', 'in', order.picking_ids.ids),
    #                     ('company_id.anglo_saxon_accounting', '=', True),
    #                     ('product_id.categ_id.property_valuation', '=', 'real_time')
    #                 ])
    #                 for move in stock_moves:
    #                     exp_key = move.product_id._get_product_accounts()['expense']
    #                     out_key = move.product_id.categ_id.property_stock_account_output_categ_id
    #                     amount = -sum(move.sudo().stock_valuation_layer_ids.mapped('value'))
    #                     stock_expense[exp_key] = self._update_amounts(stock_expense[exp_key], {'amount': amount}, move.picking_id.date, force_company_currency=True)
    #                     if move.location_id.usage == 'customer':
    #                         stock_return[out_key] = self._update_amounts(stock_return[out_key], {'amount': amount}, move.picking_id.date, force_company_currency=True)
    #                     else:
    #                         stock_output[out_key] = self._update_amounts(stock_output[out_key], {'amount': amount}, move.picking_id.date, force_company_currency=True)
    #
    #             if self.config_id.cash_rounding:
    #                 diff = order.amount_paid - order.amount_total
    #                 rounding_difference = self._update_amounts(rounding_difference, {'amount': diff}, order.date_order)
    #
    #             # Increasing current partner's customer_rank
    #             partners = (order.partner_id | order.partner_id.commercial_partner_id)
    #             partners._increase_rank('customer_rank')
    #
    #     if self.company_id.anglo_saxon_accounting:
    #         global_session_pickings = self.picking_ids.filtered(lambda p: not p.pos_order_id)
    #         if global_session_pickings:
    #             stock_moves = self.env['stock.move'].sudo().search([
    #                 ('picking_id', 'in', global_session_pickings.ids),
    #                 ('company_id.anglo_saxon_accounting', '=', True),
    #                 ('product_id.categ_id.property_valuation', '=', 'real_time'),
    #             ])
    #             for move in stock_moves:
    #                 exp_key = move.product_id._get_product_accounts()['expense']
    #                 out_key = move.product_id.categ_id.property_stock_account_output_categ_id
    #                 amount = -sum(move.stock_valuation_layer_ids.mapped('value'))
    #                 stock_expense[exp_key] = self._update_amounts(stock_expense[exp_key], {'amount': amount}, move.picking_id.date)
    #                 if move.location_id.usage == 'customer':
    #                     stock_return[out_key] = self._update_amounts(stock_return[out_key], {'amount': amount}, move.picking_id.date)
    #                 else:
    #                     stock_output[out_key] = self._update_amounts(stock_output[out_key], {'amount': amount}, move.picking_id.date)
    #     MoveLine = self.env['account.move.line'].with_context(check_move_validity=False)
    #
    #     data.update({
    #         'taxes':                               taxes,
    #         'sales':                               sales,
    #         'stock_expense':                       stock_expense,
    #         'split_receivables':                   split_receivables,
    #         'combine_receivables':                 combine_receivables,
    #         'split_receivables_cash':              split_receivables_cash,
    #         'combine_receivables_cash':            combine_receivables_cash,
    #         'invoice_receivables':                 invoice_receivables,
    #         'stock_return':                        stock_return,
    #         'stock_output':                        stock_output,
    #         'order_account_move_receivable_lines': order_account_move_receivable_lines,
    #         'rounding_difference':                 rounding_difference,
    #         'MoveLine':                            MoveLine
    #     })
    #
    #     # for key, amounts in combine_receivables.items():
    #     #     print(key, amounts)
    #     #     amounts['amount_converted'] = amounts.get('amount_converted') / payment.currency.rate
    #     # print('hello')
    #     return data

    # payment.currency.rate
# #
#     def _set_next_sequence(self):
#         pass

class MOveInh(models.Model):
    _inherit = 'mrp.production'

    @api.onchange('picking_type_id')
    def onchange_picking_type(self):
        location = self.env.ref('stock.stock_location_stock')
        try:
            location.check_access_rule('read')
        except (AttributeError, AccessError):
            location = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)],
                                                          limit=1).lot_stock_id
        self.move_raw_ids.update({'picking_type_id': self.picking_type_id})
        self.move_finished_ids.update({'picking_type_id': self.picking_type_id})
        self.location_src_id = self.picking_type_id.default_location_src_id.id or location.id
        # self.location_dest_id = self.picking_type_id.default_location_dest_id.id or location.id

    @api.model
    def _get_default_location_dest_id(self):
        location = False
        # company_id = self.env.context.get('default_company_id', self.env.company.id)
        # if self._context.get('default_picking_type_id'):
        #     location = self.env['stock.picking.type'].browse(
        #         self.env.context['default_picking_type_id']).default_location_dest_id
        # if not location:
        #     location = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1).lot_stock_id
        print('hello')
        return False

    location_dest_id = fields.Many2one(
            'stock.location', 'Finished Products Location',
            default=_get_default_location_dest_id,
            readonly=True, required=True,
            domain="[('usage','=','internal'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
            states={'draft': [('readonly', False)]}, check_company=True,
            help="Location where the system will stock the finished products.")


class BomLineInh(models.Model):
    _inherit = 'mrp.bom.line'

    location_id = fields.Many2one('stock.location')


class StockMoveInh(models.Model):
    _inherit = 'stock.move'

    bom_location_id = fields.Many2one('stock.location', related='bom_line_id.location_id')
    pick_location_id = fields.Many2one('stock.location')

    # def _action_assign(self):
    #     res = super(StockMoveInh, self)._action_assign()
    #     for move in self.filtered(lambda x: x.production_id or x.raw_material_production_id):
    #         if move.move_line_ids:
    #             move.move_line_ids.write({'production_id': move.raw_material_production_id.id,'location_id': move.pick_location_id.id,
    #                                            'workorder_id': move.workorder_id.id,})
    #     return res

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        self.ensure_one()
        # apply putaway
        location_dest_id = self.location_dest_id._get_putaway_strategy(self.product_id).id or self.location_dest_id.id

        vals = {
            'move_id': self.id,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'location_id': self.location_id.id,
            'location_dest_id': location_dest_id,
            'picking_id': self.picking_id.id,
            'company_id': self.company_id.id,
        }
        if quantity:
            rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            uom_quantity = self.product_id.uom_id._compute_quantity(quantity, self.product_uom, rounding_method='HALF-UP')
            uom_quantity = float_round(uom_quantity, precision_digits=rounding)
            uom_quantity_back_to_product_uom = self.product_uom._compute_quantity(uom_quantity, self.product_id.uom_id, rounding_method='HALF-UP')
            if float_compare(quantity, uom_quantity_back_to_product_uom, precision_digits=rounding) == 0:
                vals = dict(vals, product_uom_qty=uom_quantity)
            else:
                vals = dict(vals, product_uom_qty=quantity, product_uom_id=self.product_id.uom_id.id)
        if reserved_quant:
            vals = dict(
                vals,
                location_id=reserved_quant.location_id.id,
                lot_id=reserved_quant.lot_id.id or False,
                package_id=reserved_quant.package_id.id or False,
                owner_id =reserved_quant.owner_id.id or False,
            )
        # print(vals)
        # print(self.production_id)
        # self.raw_material_production_id.name
        if self.raw_material_production_id:
            vals.update({'location_id': self.pick_location_id.id if self.pick_location_id.id else self.bom_location_id.id})
        print(vals)
        return vals

    def _action_assign(self):
        """ Reserve stock moves by creating their stock move lines. A stock move is
        considered reserved once the sum of `product_qty` for all its move lines is
        equal to its `product_qty`. If it is less, the stock move is considered
        partially available.
        """
        StockMove = self.env['stock.move']
        assigned_moves_ids = OrderedSet()
        partially_available_moves_ids = OrderedSet()
        # Read the `reserved_availability` field of the moves out of the loop to prevent unwanted
        # cache invalidation when actually reserving the move.
        reserved_availability = {move: move.reserved_availability for move in self}
        roundings = {move: move.product_id.uom_id.rounding for move in self}
        move_line_vals_list = []
        for move in self.filtered(lambda m: m.state in ['confirmed', 'waiting', 'partially_available']):
            rounding = roundings[move]
            missing_reserved_uom_quantity = move.product_uom_qty - reserved_availability[move]
            missing_reserved_quantity = move.product_uom._compute_quantity(missing_reserved_uom_quantity, move.product_id.uom_id, rounding_method='HALF-UP')
            if move._should_bypass_reservation():
                # create the move line(s) but do not impact quants
                if move.product_id.tracking == 'serial' and (move.picking_type_id.use_create_lots or move.picking_type_id.use_existing_lots):
                    for i in range(0, int(missing_reserved_quantity)):
                        move_line_vals_list.append(move._prepare_move_line_vals(quantity=1))
                else:
                    to_update = move.move_line_ids.filtered(lambda ml: ml.product_uom_id == move.product_uom and
                                                            ml.location_id == move.location_id and
                                                            ml.location_dest_id == move.location_dest_id and
                                                            ml.picking_id == move.picking_id and
                                                            not ml.lot_id and
                                                            not ml.package_id and
                                                            not ml.owner_id)
                    if to_update:
                        to_update[0].product_uom_qty += missing_reserved_uom_quantity
                    else:
                        move_line_vals_list.append(move._prepare_move_line_vals(quantity=missing_reserved_quantity))
                assigned_moves_ids.add(move.id)
            else:
                if float_is_zero(move.product_uom_qty, precision_rounding=move.product_uom.rounding):
                    assigned_moves_ids.add(move.id)
                elif not move.move_orig_ids:
                    if move.procure_method == 'make_to_order':
                        continue
                    # If we don't need any quantity, consider the move assigned.
                    need = missing_reserved_quantity
                    if float_is_zero(need, precision_rounding=rounding):
                        assigned_moves_ids.add(move.id)
                        continue
                    # Reserve new quants and create move lines accordingly.
                    forced_package_id = move.package_level_id.package_id or None
                    if self.raw_material_production_id:
                        available_quantity = move._get_available_quantity(move.pick_location_id if move.pick_location_id else move.bom_location_id, package_id=forced_package_id)
                    else:
                        available_quantity = move._get_available_quantity(move.location_id, package_id=forced_package_id)
                    if available_quantity <= 0:
                        continue
                    if self.raw_material_production_id:
                        taken_quantity = move._update_reserved_quantity(need, available_quantity, move.pick_location_id if move.pick_location_id else move.bom_location_id, package_id=forced_package_id, strict=False)
                    else:
                        taken_quantity = move._update_reserved_quantity(need, available_quantity, move.location_id, package_id=forced_package_id, strict=False)
                    if float_is_zero(taken_quantity, precision_rounding=rounding):
                        continue
                    if float_compare(need, taken_quantity, precision_rounding=rounding) == 0:
                        assigned_moves_ids.add(move.id)
                    else:
                        partially_available_moves_ids.add(move.id)
                else:
                    # Check what our parents brought and what our siblings took in order to
                    # determine what we can distribute.
                    # `qty_done` is in `ml.product_uom_id` and, as we will later increase
                    # the reserved quantity on the quants, convert it here in
                    # `product_id.uom_id` (the UOM of the quants is the UOM of the product).
                    move_lines_in = move.move_orig_ids.filtered(lambda m: m.state == 'done').mapped('move_line_ids')
                    keys_in_groupby = ['location_dest_id', 'lot_id', 'result_package_id', 'owner_id']

                    def _keys_in_sorted(ml):
                        return (ml.location_dest_id.id, ml.lot_id.id, ml.result_package_id.id, ml.owner_id.id)

                    grouped_move_lines_in = {}
                    for k, g in groupby(sorted(move_lines_in, key=_keys_in_sorted), key=itemgetter(*keys_in_groupby)):
                        qty_done = 0
                        for ml in g:
                            qty_done += ml.product_uom_id._compute_quantity(ml.qty_done, ml.product_id.uom_id)
                        grouped_move_lines_in[k] = qty_done
                    move_lines_out_done = (move.move_orig_ids.mapped('move_dest_ids') - move)\
                        .filtered(lambda m: m.state in ['done'])\
                        .mapped('move_line_ids')
                    # As we defer the write on the stock.move's state at the end of the loop, there
                    # could be moves to consider in what our siblings already took.
                    moves_out_siblings = move.move_orig_ids.mapped('move_dest_ids') - move
                    moves_out_siblings_to_consider = moves_out_siblings & (StockMove.browse(assigned_moves_ids) + StockMove.browse(partially_available_moves_ids))
                    reserved_moves_out_siblings = moves_out_siblings.filtered(lambda m: m.state in ['partially_available', 'assigned'])
                    move_lines_out_reserved = (reserved_moves_out_siblings | moves_out_siblings_to_consider).mapped('move_line_ids')
                    keys_out_groupby = ['location_id', 'lot_id', 'package_id', 'owner_id']

                    def _keys_out_sorted(ml):
                        return (ml.location_id.id, ml.lot_id.id, ml.package_id.id, ml.owner_id.id)

                    grouped_move_lines_out = {}
                    for k, g in groupby(sorted(move_lines_out_done, key=_keys_out_sorted), key=itemgetter(*keys_out_groupby)):
                        qty_done = 0
                        for ml in g:
                            qty_done += ml.product_uom_id._compute_quantity(ml.qty_done, ml.product_id.uom_id)
                        grouped_move_lines_out[k] = qty_done
                    for k, g in groupby(sorted(move_lines_out_reserved, key=_keys_out_sorted), key=itemgetter(*keys_out_groupby)):
                        grouped_move_lines_out[k] = sum(self.env['stock.move.line'].concat(*list(g)).mapped('product_qty'))
                    available_move_lines = {key: grouped_move_lines_in[key] - grouped_move_lines_out.get(key, 0) for key in grouped_move_lines_in.keys()}
                    # pop key if the quantity available amount to 0
                    available_move_lines = dict((k, v) for k, v in available_move_lines.items() if v)

                    if not available_move_lines:
                        continue
                    for move_line in move.move_line_ids.filtered(lambda m: m.product_qty):
                        if available_move_lines.get((move_line.location_id, move_line.lot_id, move_line.result_package_id, move_line.owner_id)):
                            available_move_lines[(move_line.location_id, move_line.lot_id, move_line.result_package_id, move_line.owner_id)] -= move_line.product_qty
                    for (location_id, lot_id, package_id, owner_id), quantity in available_move_lines.items():
                        need = move.product_qty - sum(move.move_line_ids.mapped('product_qty'))
                        # `quantity` is what is brought by chained done move lines. We double check
                        # here this quantity is available on the quants themselves. If not, this
                        # could be the result of an inventory adjustment that removed totally of
                        # partially `quantity`. When this happens, we chose to reserve the maximum
                        # still available. This situation could not happen on MTS move, because in
                        # this case `quantity` is directly the quantity on the quants themselves.
                        available_quantity = move._get_available_quantity(location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=True)
                        if float_is_zero(available_quantity, precision_rounding=rounding):
                            continue
                        taken_quantity = move._update_reserved_quantity(need, min(quantity, available_quantity), location_id, lot_id, package_id, owner_id)
                        if float_is_zero(taken_quantity, precision_rounding=rounding):
                            continue
                        if float_is_zero(need - taken_quantity, precision_rounding=rounding):
                            assigned_moves_ids.add(move.id)
                            break
                        partially_available_moves_ids.add(move.id)
            if move.product_id.tracking == 'serial':
                move.next_serial_count = move.product_uom_qty

        self.env['stock.move.line'].create(move_line_vals_list)
        StockMove.browse(partially_available_moves_ids).write({'state': 'partially_available'})
        StockMove.browse(assigned_moves_ids).write({'state': 'assigned'})
        self.mapped('picking_id')._check_entire_pack()
