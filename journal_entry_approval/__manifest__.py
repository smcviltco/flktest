# -*- coding: utf-8 -*-
{
    'name': "Journal Entry Approval",

    'summary': """
        This Module Covers up Two Level Approval On Journal Entry's Document""",

    'description': """
        This Module Covers up Two Level Approval On Journal Entry's Document
    """,

    'author': "Viltco",
    'website': "http://www.viltco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '14.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'security/security.xml',
        'views/account_move_views.xml',
    ],

}
