# -*- coding: utf-8 -*-


from xml import etree
from lxml import etree
from odoo.exceptions import UserError, ValidationError, Warning
from datetime import datetime
from datetime import date
from odoo import api, fields, models, _


class ProductGroup(models.Model):
    _name = 'product.group'
    _description = 'Product Group'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', tracking=True)
    categ_id = fields.Many2one('product.category', string='Product Category', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', tracking=True)


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    product_group_id = fields.Many2one('product.group', string='Product Group', tracking=True)


class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    product_group_id = fields.Many2one('product.group',
                                       string='Product Group',
                                       related='product_tmpl_id.product_group_id',
                                       tracking=True,
                                       store=True)

