# -*- coding: utf-8 -*-
{
    'name': "Cairopac Product Category Type",

    'summary': 'Cairopack product category',
    'author': 'iSky Development Team',
    'website': 'http://www.iskydev.com',
    'description': ''' ''',

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'sale', 'purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/security.xml',
        'views/product_category.xml',
        'views/sale_order.xml',
        'views/purchase.xml',
        'views/stock.xml',
        'views/account_move.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
