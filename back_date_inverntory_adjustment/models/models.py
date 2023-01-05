from odoo import fields, models
from datetime import datetime

from odoo.exceptions import UserError


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    inventory_check = fields.Boolean()
    back_date = fields.Datetime()

    def action_update_lines(self):
        if self.inventory_check:
            if not self.back_date:
                raise UserError('Please Select a Back Date.')
            self._get_inventory_lines_values()
            for move in self.move_ids:
                move.date = self.back_date
                for m in move.stock_valuation_layer_ids:
                    self.env.cr.execute(
                        "UPDATE stock_valuation_layer set create_date = '%s' WHERE id=%s" % (self.back_date, m.id))
                for move_line in move.move_line_ids:
                    move_line.date = self.back_date
                # account_moves = self.env['account.move'].search([('stock_move_id.id', 'in', self.move_ids.ids)]) stock_valuation_layer_ids
                # for m in account_moves:
                #     m.date = self.back_date
                # print(account_moves)

    def post_inventory(self):
        res = super(StockInventory, self).post_inventory()
        if self.inventory_check:
            if not self.back_date:
                raise UserError('Please Select a Back Date.')
            for move in self.move_ids:
                move.date = self.back_date
                for move_line in move.move_line_ids:
                    move_line.date = self.back_date
        return res

    # def post_inventory(self):
    #     rec = self.mapped('move_ids').filtered(lambda move: move.state != 'done')._action_done()
    #     if self.inventory_check:
    #         rec.date = self.back_date
    #         move_line = self.env['stock.move.line'].search([('move_id', '=', rec.id)])
    #         move_line.date = self.back_date
    #     return True

    def _get_inventory_lines_values(self):
        """Return the values of the inventory lines to create for this inventory.

        :return: a list containing the `stock.inventory.line` values to create
        :rtype: list
        """
        self.ensure_one()
        quants_groups = self._get_quantities()
        vals = []
        for (product_id, location_id, lot_id, package_id, owner_id), quantity in quants_groups.items():
            line_values = {
                'inventory_id': self.id,
                'product_qty': 0 if self.prefill_counted_quantity == "zero" else quantity,
                'theoretical_qty': quantity,
                'prod_lot_id': lot_id,
                'partner_id': owner_id,
                'product_id': product_id,
                'location_id': location_id,
                'package_id': package_id,
                'inventory_date': self.back_date if self.inventory_check else datetime.today(),
            }
            line_values['product_uom_id'] = self.env['product.product'].browse(product_id).uom_id.id
            vals.append(line_values)
        if self.exhausted:
            vals += self._get_exhausted_inventory_lines_vals({(l['product_id'], l['location_id']) for l in vals})
        return vals
