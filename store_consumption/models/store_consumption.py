from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class StoreConsumption(models.Model):
    _name = 'store.consumption'
    _description = 'Store Consumption'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    _rec_name = 'location_id'

    def _default_location_id(self):
        records = self.env['stock.location'].search([('is_store_location', '=', True)])
        return records

    # def _default_account_id(self):
    #     records = self.env['account.account'].search([('cgs_account', '=', True)])
    #     return records

    ref = fields.Char('Ref', copy=False, default='New', tracking=True)
    location_id = fields.Many2one('stock.location', string="Location", tracking=True, default=_default_location_id)
    account_id = fields.Many2one('account.account', string="Account", tracking=True,
                                 domain="[('cgs_account','=',True)]")
    date = fields.Date('Date' ,tracking=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('to_review', 'Review'),
                              ('posted', 'Posted')],
                             tracking=True, default='draft')

    stock_consumption_lines = fields.One2many('store.consumption.line', 'store_consumption_id')

    @api.model
    def create(self, values):
        seq = self.env['ir.sequence'].search([('name', '=', 'Store Consumption')])
        self.env['ir.sequence'].next_by_code(seq.code)
        if datetime.now().month <= 9:
            print("jjj")
            values['ref'] = seq.prefix + '/' + str(datetime.now().year) + '/' + '0' + str(
                datetime.now().month) + '/' + '000' + str(
                seq.number_next_actual) or _('New')
        else:
            print("mmmm")
            values['ref'] = seq.prefix + '/' + str(datetime.now().year) + '/' + str(
                datetime.now().month) + '/' + '000' + str(
                seq.number_next_actual) or _('New')
        res = super(StoreConsumption, self).create(values)
        return res

    def action_to_review(self):
        self.write({
            'state': 'to_review'
        })

    def action_posted(self):
        picking_delivery = self.env['stock.picking.type'].search([('code', '=', 'internal')], limit=1)
        records = self.env['stock.location'].search([('is_consumption_location', '=', True)])
        vals = {
            'picking_type_id': picking_delivery.id,
            'location_id': self.location_id.id,
            'location_dest_id': records.id,
            'origin': self.ref,
            # 'state': 'done',
        }
        picking = self.env['stock.picking'].create(vals)
        check = False
        lines = []
        move_dict = []
        for r in self.stock_consumption_lines:
            qty = 0
            if r.available_quantity:
                if r.qty > r.available_quantity:
                    print("available...",r.available_quantity)
                    qty = r.available_quantity
                    print("rrrrrrr",qty)
                else:
                    print("tyyyyy...",r.qty)
                    qty = r.qty
                check = True
                line = {
                    'picking_id': picking.id,
                    'product_id': r.product_id.id,
                    'name': r.product_id.name,
                    'product_uom': r.product_id.uom_id.id,
                    'location_id': self.location_id.id,
                    'location_dest_id': records.id,
                    'product_uom_qty': r.qty,
                    'quantity_done': qty,
                }
                stock_move = self.env['stock.move'].create(line)
                journal = self.env['account.journal'].search([('is_stock_journal', '=', True)])
                account = self.env['account.account'].search([('is_stock_account', '=', True)])
                move_dict = {
                    'ref': self.ref,
                    # 'branch_id': li.branch_id.id,
                    'move_type': 'entry',
                    'journal_id': journal.id,
                    'date': self.date,
                    'state': 'draft',
                }
                debit_line = (0, 0, {
                    'name': f'Store Consumption {r.product_id.name}',
                    'debit': r.product_id.standard_price * r.qty,
                    'credit': 0.0,
                    # 'partner_id': li.brand_id.vendor_id.id,
                    'account_id': self.account_id.id,
                })
                lines.append(debit_line)
                credit_line = (0, 0, {
                    'name': f'Store Consumption {r.product_id.name}',
                    'debit': 0.0,
                    # 'partner_id': r.partner_id.id,
                    'credit': r.product_id.standard_price * r.qty,
                    'account_id': account.id,
                })
                lines.append(credit_line)
                move_dict['line_ids'] = lines
        move = self.env['account.move'].create(move_dict)
        picking.action_confirm()
        picking.action_assign()
        picking.button_validate()
        move.action_post()
        # move.button_review()
        # move.button_approved()
        # move.action_post()
        print(move)
        self.state = 'posted'
        if not check:
            raise UserError(
                f'Cannot validate this consumption. Kindly make the products available at Store Location.')

    int_counter = fields.Integer(compute='get_int_counter')

    def get_int_counter(self):
        for rec in self:
            count = self.env['stock.picking'].search_count([('origin', '=', self.ref)])
            rec.int_counter = count

    def get_internal_transfer(self):
        return {
            'name': _('Transfers'),
            'domain': [('origin', '=', self.ref)],
            'view_type': 'form',
            'res_model': 'stock.picking',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    jv_counter = fields.Integer(compute='get_jv_counter')

    def get_jv_counter(self):
        for rec in self:
            count = self.env['account.move'].search_count([('ref', '=', self.ref)])
            rec.jv_counter = count

    def get_jv(self):
        return {
            'name': _('Journal Entry'),
            'domain': [('ref', '=', self.ref)],
            'view_type': 'form',
            'res_model': 'account.move',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }


class StoreConsumptionLines(models.Model):
    _name = 'store.consumption.line'
    _description = 'Store Consumption Lines'

    product_id = fields.Many2one('product.product', string="Product", tracking=True)
    available_quantity = fields.Float(string='Available Quantity', store=True, compute="_compute_available_quantity")
    uom = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        required=True, related='product_id.uom_id'
    )
    qty = fields.Integer('Qty Consumed' ,tracking=True)

    store_consumption_id = fields.Many2one('store.consumption', string="Consumption Lines", tracking=True)

    @api.constrains('available_quantity', 'qty')
    def _check_qunatity(self):
        for rec in self:
            if rec.qty > rec.available_quantity:
                raise ValidationError(_("Qty consumed should be less than or equal to available Qty."))

    @api.depends('product_id', 'store_consumption_id.location_id')
    def _compute_available_quantity(self):
        for rec in self:
            total = 0
            quants = self.get_quant_lines()
            quants = self.env['stock.quant'].browse(quants)
            for q_line in quants:
                if q_line.product_tmpl_id.name == rec.product_id.name and q_line.location_id.id == rec.store_consumption_id.location_id.id:
                    total = total + q_line.available_quantity
            rec.available_quantity = total

    def get_quant_lines(self):
        domain_loc = self.env['product.product']._get_domain_locations()[0]
        quant_ids = [l['id'] for l in self.env['stock.quant'].search_read(domain_loc, ['id'])]
        return quant_ids
