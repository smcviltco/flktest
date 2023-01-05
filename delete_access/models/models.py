from odoo import api, fields, models
from lxml import etree


class SaleOrderDelete(models.Model):
    _inherit = "sale.order"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(SaleOrderDelete, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if not self.env.user.has_group('create_access.group_delete_access'):
            temp = etree.fromstring(result['arch'])
            temp.set('delete', '0')
            result['arch'] = etree.tostring(temp)
        return result


class PurchaseOrderDelete(models.Model):
    _inherit = "purchase.order"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(PurchaseOrderDelete, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if not self.env.user.has_group('delete_access.group_delete_access'):
            temp = etree.fromstring(result['arch'])
            temp.set('delete', '0')
            result['arch'] = etree.tostring(temp)
        return result


class AccountDelete(models.Model):
    _inherit = "account.move"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(AccountDelete, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if not self.env.user.has_group('delete_access.group_delete_access'):
            temp = etree.fromstring(result['arch'])
            temp.set('delete', '0')
            result['arch'] = etree.tostring(temp)
        return result


class AccountPaymentDelete(models.Model):
    _inherit = "account.payment"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(AccountPaymentDelete, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if not self.env.user.has_group('delete_access.group_delete_access'):
            temp = etree.fromstring(result['arch'])
            temp.set('delete', '0')
            result['arch'] = etree.tostring(temp)
        return result


class ProductDelete(models.Model):
    _inherit = "product.product"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(ProductDelete, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if not self.env.user.has_group('delete_access.group_delete_access'):
            temp = etree.fromstring(result['arch'])
            temp.set('delete', '0')
            result['arch'] = etree.tostring(temp)
        return result

class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(ProductTemplate, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if not self.env.user.has_group('delete_access.group_delete_access'):
            temp = etree.fromstring(result['arch'])
            temp.set('delete', '0')
            result['arch'] = etree.tostring(temp)
        return result

