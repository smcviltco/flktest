# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'General Expenses',
    'author': 'Viltco',
    'summary': 'Managing General Expenses',
    'version': '1',
    'depends': ['base','account'],
    'data': [ 
		'templates.xml',
		"security/security.xml",
		"security/ir.model.access.csv",
		],
    'installable': True,
    'auto_install': False
}
