# -*- encoding: utf-8 -*-
{
    'name': 'Cairopack Purchase Request',
    'summary': 'Cairopack Purchase Request',
    'author': 'iSky Development Team',
    'website': 'http://www.iskydev.com',
    'description': '''
        This module edit in purchase and inventory modules.
     ''',
    'depends': ['base', 'hr', 'purchase_requisition', 'purchase_stock', 'stock_account', 'product','sale','account','delivery','stock','purchase','mrp'],

    'data': [
        # security
        'security/groups.xml',
        'security/ir.model.access.csv',
        # views
        'views/product_inherit_view.xml',
        'views/purchase_request_view.xml',
        'views/stock_picking_inherit_view.xml',
        'views/menu_items_view.xml',
        'views/purchase_order_inhirit.xml',
        'views/purchase_requisition_inhirit.xml',
        'views/sale_order_view.xml',
        'views/account_move_view.xml',
        # reports
        'reports/purchase_order.xml',
        'reports/report.xml',
        'reports/template.xml',

    ]
}
