# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplateInh(models.Model):
    _inherit = 'product.template'

    company_id = fields.Many2one('res.company', 'Company', index=True, default=lambda self: self.env.company.id, readonly=True)


class ResPartnerInh(models.Model):
    _inherit = 'res.partner'

    company_id = fields.Many2one('res.company', 'Company', index=True, default=lambda self: self.env.company.id, readonly=True)


class ProductCategoryInh(models.Model):
    _inherit = 'product.category'

    company_id = fields.Many2one('res.company', 'Company', index=True, default=lambda self: self.env.company.id)
