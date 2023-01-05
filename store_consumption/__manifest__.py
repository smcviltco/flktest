# -*- coding: utf-8 -*-
{
    'name': "Store Consumption",

    'summary': """
            Store Consumption
        """,

    'description': """
        Store Consumption
    """,

    'author': "Musadiq Fiaz Chaudhary",
    'website': "http://www.viltco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'stock',
    'version': '14.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base' , 'stock' , 'account' , 'product' , 'uom' , 'journal_entry_approval'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/data.xml',
        'views/stock_consumption.xml',
        'views/inherited_models.xml',
    ],

}
