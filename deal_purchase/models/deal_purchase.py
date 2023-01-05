from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

from odoo.tools import float_compare


class DealPurchase(models.Model):
    _name = 'deal.purchase'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'ref'

    ref = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'),
                      tracking=True)
    vendor_id = fields.Many2one('res.partner', string="Vendor", tracking=True)
    date = fields.Date(string='Date', tracking=True, required=True)

    quantity = fields.Float()
    received_quantity = fields.Float()
    balance = fields.Float(compute='_compute_balance')

    vendor_reference = fields.Char(string='Vendor Reference', tracking=True)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('closed', 'Closed'), ('cancel', 'Cancelled')], default='draft',
                             string="Status", tracking=True)

    deal_lines_id = fields.One2many('deal.lines', 'deal_id')
    transfer_lines = fields.One2many('transfer.lines', 'deal_id')
    production_lines = fields.One2many('production.lines', 'deal_id')

    @api.depends('deal_lines_id', 'deal_lines_id.qty', 'deal_lines_id.received_qty')
    def _compute_balance(self):
        for rec in self:
            quantity = 0
            received_quantity = 0
            for line in rec.deal_lines_id:
                quantity = quantity + line.qty
                received_quantity = received_quantity + line.received_qty
            rec.quantity = quantity
            rec.received_quantity = received_quantity
            rec.balance = quantity - received_quantity

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '%s : %s' % (rec.ref, rec.vendor_id.name)))
        return res

    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('deal.purchase') or _('New')  # get seq. like : 'SO111'
        reference = str(vals['ref']).replace('DE', '')
        d1 = datetime.strptime(str(vals['date']), "%Y-%m-%d").date()
        your_new_so_name = f'DE/{d1.year}/{d1.month}/{reference}'
        vals.update({'ref': your_new_so_name})
        return super(DealPurchase, self).create(vals)

    def write(self, vals):
        if 'date' in vals:
            print(self.ref)
            reference = self.ref.split('/')
            print(reference[3])
            d1 = datetime.strptime(str(vals['date']), "%Y-%m-%d")
            your_new_so_name = f'DE/{d1.year}/{d1.month}/{reference[3]}'
            vals.update({'ref': your_new_so_name})
        return super(DealPurchase, self).write(vals)

    def action_close(self):
        self.state = 'closed'

    def action_confirm(self):
        self.state = 'confirm'

    def action_reset_draft(self):
        self.state = 'draft'

    def action_cancel(self):
        self.state = 'cancel'

    def unlink(self):
        for s in self:
            if s.state not in ('draft', 'cancel'):
                raise UserError(
                    'You cannot delete which is not in draft or cancelled state')
        return super(DealPurchase, self).unlink()


class ProductionLines(models.Model):
    _name = 'production.lines'

    product_id = fields.Many2one('product.product', string="Product")
    # partner_id = fields.Many2one('res.partner')
    # location_dest_id = fields.Many2one('stock.location')
    ref = fields.Char('Production Ref')
    origin = fields.Char('Source Document')
    qty = fields.Float('Quantity')
    uom_id = fields.Many2one('uom.uom')

    deal_id = fields.Many2one('deal.purchase')


class TransferLines(models.Model):
    _name = 'transfer.lines'

    product_id = fields.Many2one('product.product', string="Product")
    partner_id = fields.Many2one('res.partner')
    location_dest_id = fields.Many2one('stock.location')
    ref = fields.Char('Transfer Ref')
    origin = fields.Char('Source Document')
    qty = fields.Float('Quantity')
    deal_id = fields.Many2one('deal.purchase')


class DealLines(models.Model):
    _name = 'deal.lines'

    product_id = fields.Many2one('product.template', string="Product")
    description = fields.Char('Description')
    qty = fields.Float('Quantity')
    received_qty = fields.Float('Quantity Received', compute="_compute_received_quantity")
    unit_price = fields.Float('Unit Price')
    sub_total = fields.Float('SubTotal', readonly=True)

    deal_id = fields.Many2one('deal.purchase')

    @api.onchange('qty', 'unit_price', 'sub_total')
    def _function_subtotal(self):
        for rec in self:
            rec.sub_total = rec.qty * rec.unit_price

    # @api.depends('product_id')
    def _compute_received_quantity(self):
        for rec in self:
            # record = self.env['stock.picking'].search([('deal_id', '=', rec.deal_id.ref), ('picking_type_id.code', '=', 'incoming'), ('state', '=', 'done')])
            # returns = self.env['stock.picking'].search(
            #     [('deal_id', '=', rec.deal_id.ref), ('picking_type_id.code', '=', 'outgoing'), ('state', '=', 'done')])
            # r = 0
            # s = 0
            # for l in record.move_ids_without_package:
            #     r = r + l.qty_kg
            # for i in returns.move_ids_without_package:
            #     s = s + i.qty_kg
            #
            # rec.received_qty = r - s
            transfer_qty = 0
            if rec.deal_id.transfer_lines:
                for line in rec.deal_id.transfer_lines:
                    if line.product_id.product_tmpl_id.id == rec.product_id.id:
                        transfer_qty = transfer_qty + line.qty
                # rec.received_qty = transfer_qty

            qty = 0
            if rec.deal_id.production_lines:
                for line in rec.deal_id.production_lines:
                    if line.product_id.product_tmpl_id.id == rec.product_id.id:
                        qty = qty + line.qty

            rec.received_qty = transfer_qty + qty


class PurchaseOrderDeal(models.Model):
    _inherit = "purchase.order"

    deal_id = fields.Many2one('deal.purchase', string='Deals')
    vendor = fields.Char(compute='_compute_vendor')
    vendor_ref = fields.Char(readonly=1)

    @api.depends('deal_id')
    def _compute_vendor(self):
        if self.deal_id:
            self.vendor = self.deal_id.vendor_id.name
            self.vendor_ref = self.deal_id.vendor_reference
        else:
            self.vendor = ''

    def button_confirm(self):
        res = super(PurchaseOrderDeal, self).button_confirm()
        for rec in self:
            for pick_rec in rec.picking_ids:
                pick_rec.write({
                    'deal_id': rec.deal_id.ref
                })
            for r in rec.order_line:
                for i in pick_rec.move_ids_without_package:
                    i.write({
                        'qty_kg': r.qty_kg
                    })
        return res


class MrpImmediateProductionInh(models.TransientModel):
    _inherit = 'mrp.immediate.production'

    def process(self):
        productions_to_do = self.env['mrp.production']
        productions_not_to_do = self.env['mrp.production']
        for line in self.immediate_production_line_ids:
            if line.to_immediate is True:
                productions_to_do |= line.production_id
            else:
                productions_not_to_do |= line.production_id

        for production in productions_to_do:
            error_msg = ""
            if production.product_tracking in ('lot', 'serial') and not production.lot_producing_id:
                production.action_generate_serial()
            if production.product_tracking == 'serial' and float_compare(production.qty_producing, 1,
                                                                         precision_rounding=production.product_uom_id.rounding) == 1:
                production.qty_producing = 1
            else:
                production.qty_producing = production.product_qty - production.qty_produced
            production._set_qty_producing()
            for move in production.move_raw_ids.filtered(lambda m: m.state not in ['done', 'cancel']):
                rounding = move.product_uom.rounding
                for move_line in move.move_line_ids:
                    if move_line.product_uom_qty:
                        move_line.qty_done = min(move_line.product_uom_qty, move_line.move_id.should_consume_qty)
                    if float_compare(move.quantity_done, move.should_consume_qty, precision_rounding=rounding) >= 0:
                        break
                if float_compare(move.product_uom_qty, move.quantity_done,
                                 precision_rounding=move.product_uom.rounding) == 1:
                    if move.has_tracking in ('serial', 'lot'):
                        error_msg += "\n  - %s" % move.product_id.display_name

            if error_msg:
                error_msg = _('You need to supply Lot/Serial Number for products:') + error_msg
                raise UserError(error_msg)

        productions_to_validate = self.env.context.get('button_mark_done_production_ids')
        if productions_to_validate:
            productions_to_validate = self.env['mrp.production'].browse(productions_to_validate)
            productions_to_validate = productions_to_validate - productions_not_to_do
            productions_to_validate.action_deals()
            return productions_to_validate.with_context(skip_immediate=True).button_mark_done()
        return True


class MrpProductionInh(models.Model):
    _inherit = "mrp.production"

    deal_id = fields.Many2one('deal.purchase')

    def action_deals(self):
        line_vals = []
        for line in self.move_raw_ids:
            if line.bom_location_id.display_name == 'Bulk/Stock':
                line_vals.append((0, 0, {
                    'product_id': line.product_id.id,
                    'ref': self.name,
                    'qty': line.quantity_done,
                    'uom_id': line.product_uom.id,
                }))
        self.deal_id.production_lines = line_vals

    def action_create_deal_lines(self):
        line_vals = []
        for rec in self:
            if rec.state == 'done':
                for line in rec.move_raw_ids:
                    if line.bom_location_id.display_name == 'Bulk/Stock':
                        line_vals.append((0, 0, {
                            'product_id': line.product_id.id,
                            'ref': rec.name,
                            'qty': line.quantity_done,
                            'uom_id': line.product_uom.id,
                        }))
            for i in rec.deal_id.production_lines:
                i.unlink()
            rec.deal_id.production_lines = line_vals


class StockPickingField(models.Model):
    _inherit = "stock.picking"

    deal_id = fields.Char(string='Deals', readonly=True)

    def action_create_deal_lines(self):
        line_vals = []
        for rec in self:
            if rec.purchase_id and rec.state == 'done':
                if rec.picking_type_id.code == 'outgoing' and rec.purchase_id.deal_id:
                    print("Is Return")

                    for line in rec.move_ids_without_package:
                        line_vals.append((0, 0, {
                            'product_id': line.product_id.id,
                            'partner_id': line.picking_id.partner_id.id,
                            'location_dest_id': line.picking_id.location_dest_id.id,
                            'ref': line.picking_id.name,
                            'origin': line.picking_id.origin,
                            'qty': -line.qty_kg,
                        }))

                if rec.picking_type_id.code == 'incoming' and rec.purchase_id.deal_id:
                    # line_vals = []
                    for line in rec.move_ids_without_package:
                        line_vals.append((0, 0, {
                            'product_id': line.product_id.id,
                            'partner_id': line.picking_id.partner_id.id,
                            'location_dest_id': line.picking_id.location_dest_id.id,
                            'ref': line.picking_id.name,
                            'origin': line.picking_id.origin,
                            'qty': line.qty_kg,
                        }))
            print(line_vals)
            for i in rec.purchase_id.deal_id.transfer_lines:
                i.unlink()
            rec.purchase_id.deal_id.transfer_lines = line_vals

    def create_deal_lines(self):
        for rec in self:
            if rec.purchase_id:
                if rec.picking_type_id.code == 'outgoing' and rec.purchase_id.deal_id:
                    print("Is Return")
                    line_vals = []
                    for line in rec.move_ids_without_package:
                        line_vals.append((0, 0, {
                            'product_id': line.product_id.id,
                            'partner_id': line.picking_id.partner_id.id,
                            'location_dest_id': line.picking_id.location_dest_id.id,
                            'ref': line.picking_id.name,
                            'origin': line.picking_id.origin,
                            'qty': -line.qty_kg,
                        }))
                        rec.purchase_id.deal_id.transfer_lines = line_vals
                if rec.picking_type_id.code == 'incoming' and rec.purchase_id.deal_id:
                    line_vals = []
                    for line in rec.move_ids_without_package:
                        line_vals.append((0, 0, {
                            'product_id': line.product_id.id,
                            'partner_id': line.picking_id.partner_id.id,
                            'location_dest_id': line.picking_id.location_dest_id.id,
                            'ref': line.picking_id.name,
                            'origin': line.picking_id.origin,
                            'qty': line.qty_kg,
                        }))
                    if rec.purchase_id:
                        rec.purchase_id.deal_id.transfer_lines = line_vals


class StockImmediateTransferInh(models.TransientModel):
    _inherit = 'stock.immediate.transfer'

    def process(self):
        pickings_to_do = self.env['stock.picking']
        pickings_not_to_do = self.env['stock.picking']
        for line in self.immediate_transfer_line_ids:
            if line.to_immediate is True:
                pickings_to_do |= line.picking_id
            else:
                pickings_not_to_do |= line.picking_id

        for picking in pickings_to_do:
            # If still in draft => confirm and assign
            if picking.state == 'draft':
                picking.action_confirm()
                if picking.state != 'assigned':
                    picking.action_assign()
                    if picking.state != 'assigned':
                        raise UserError(
                            _("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
            for move in picking.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
                for move_line in move.move_line_ids:
                    move_line.qty_done = move_line.product_uom_qty

        pickings_to_validate = self.env.context.get('button_validate_picking_ids')
        if pickings_to_validate:
            pickings_to_validate = self.env['stock.picking'].browse(pickings_to_validate)
            pickings_to_validate = pickings_to_validate - pickings_not_to_do
            pickings_to_validate.create_deal_lines()
            return pickings_to_validate.with_context(skip_immediate=True).button_validate()

        return True

    # def button_validate(self):
    #     line_vals =[]
    #     line_vals.append((0, 0, {
    #         'product_id': product.id,
    #         'price_unit': line.price_unit,
    #         'quantity': line.quantity,
    #         # 'account_id': line.account_id.id,
    #         # 'journal_id': journal.id,
    #         'currency_id': currency.id,
    #         'company_id': self.company_id.id,
    #         'product_uom_id': uom.id,
    #         'discount': line.discount,
    #     }))
    #     return super(PurchaseOrderLineQty, self).button_validate()


class PurchaseOrderLineQty(models.Model):
    _inherit = "purchase.order.line"

    qty_kg = fields.Float(string='Qty in Kgs')



class StockMoveLineQty(models.Model):
    _inherit = "stock.move"

    qty_kg = fields.Float(string='Qty in Kgs')




