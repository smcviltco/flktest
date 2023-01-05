from odoo import models, fields, api


class CreatePurchaseWizard(models.TransientModel):
    _name = 'create.purchase.wizard'

    company_id = fields.Many2one('res.company')
    purchase_ids = fields.Many2many('purchase.order')

    def create_data(self):
        for rec in self.purchase_ids:
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
                    'product_qty': line.product_qty,
                    'taxes_id': line.taxes_id.ids,
                    'date_planned': line.date_planned,
                    'currency_id': currency.id,
                    'company_id': self.company_id.id,
                    'product_uom': uom.id,
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
                'currency_id': currency.id,
                'date_planned': rec.date_planned,
                'date_approve': rec.date_approve,
                'order_line': line_vals,
                'partner_ref': rec.partner_ref,
                'state': 'draft',
                'company_id': self.company_id.id,
                'user_id': user.id,
                'picking_type_id': rec.picking_type_id.id,
            }
            purchase = self.env['purchase.order'].sudo().with_context(default_company_id=self.company_id.id).create(vals)
