from odoo import models, fields, api


class CreateSaleWizard(models.TransientModel):
    _name = 'create.sale.wizard'

    company_id = fields.Many2one('res.company')
    sale_ids = fields.Many2many('sale.order')

    def create_data(self):
        for rec in self.sale_ids:
            line_vals = []
            currency = self.env['res.currency'].sudo().search([('name', '=', rec.currency_id.name)])
            for line in rec.order_line:
                uom_categ = self.env['uom.category'].sudo().search([('name', '=', line.product_id.uom_id.category_id.name)])
                if not uom_categ:
                    uom_categ = self.env['uom.uom'].sudo().create({
                        'name': line.product_id.uom_id.category_id.name,
                        'company_id': self.company_id.id,
                    })
                uom = self.env['uom.uom'].sudo().search([('name', '=', line.product_id.uom_id.name)])
                if not uom:
                    uom = self.env['uom.uom'].sudo().create({
                        'name': line.product_id.uom_id.name,
                        'category_id': uom_categ.id,
                        'uom_type': line.product_id.uom_id.uom_type,
                        'active': line.product_id.uom_id.active,
                        'rounding': line.product_id.uom_id.rounding,
                        'company_id': self.company_id.id,
                    })
                uom_po = self.env['uom.uom'].sudo().search([('name', '=', line.product_id.uom_po_id.name)])
                if not uom_po:
                    uom_po = self.env['uom.uom'].sudo().create({
                        'name': line.product_id.uom_id.name,
                        'category_id': uom_categ.id,
                        'uom_type': line.product_id.uom_id.uom_type,
                        'active': line.product_id.uom_id.active,
                        'rounding': line.product_id.uom_id.rounding,
                        'company_id': self.company_id.id,
                    })
                product = self.env['product.product'].sudo().search([('name', '=', line.product_id.name), ('company_id', '=', self.company_id.id)])
                if not product:
                    product = self.env['product.product'].sudo().create({
                        'name': line.product_id.name,
                        'type': line.product_id.type,
                        'lst_price': line.product_id.lst_price,
                        'standard_price': line.product_id.standard_price,
                        'uom_id': uom.id,
                        'uom_po_id': uom_po.id,
                        'categ_id': line.product_id.categ_id.id,
                        'taxes_id': line.product_id.taxes_id.ids,
                        'company_id': self.company_id.id,
                    })
                line_vals.append((0, 0, {
                    'product_id': product.id,
                    'price_unit': line.price_unit,
                    'name': line.name,
                    'product_uom_qty': line.product_uom_qty,
                    # 'account_id': line.account_id.id,
                    # 'journal_id': journal.id,
                    'currency_id': currency.id,
                    'company_id': self.company_id.id,
                    'product_uom': uom.id,
                    'discount': line.discount,
                }))
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
                'date_order': rec.date_order,
                # 'move_type': 'out_invoice',
                'order_line': line_vals,
                'client_order_ref': rec.client_order_ref,
                'state': 'draft',
                'company_id': self.company_id.id,
                'user_id': user.id,
                # 'team_id': rec.team_id.id,
            }
            sale_order = self.env['sale.order'].sudo().with_context(default_company_id=self.company_id.id).create(vals)
            if rec.state == 'sale':
                sale_order.action_confirm()
                for pick in sale_order.picking_ids:
                    pick.button_validate()

