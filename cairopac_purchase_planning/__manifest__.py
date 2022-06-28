# -*- coding: utf-8 -*-
{
    'name': "Cairopac Purchase Planning",

    'summary': """Cairopac Purchase Planning """,

    'description': """
        This module edit on purchase to add the following : \n
            1- Add purchase plan screen .\n
    """,

    'author': "iSky Development Team",
    'website': "http://www.iskydev.com",
    'category': 'Purchase',
    'version': '0.1',
    'depends': ['base', 'purchase','mrp', 'report_xls','sale'],
    'data': [
        'data/purchase_sequence.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizard/purchase_plan_line_wizard_view.xml',
        'views/product_product_view.xml',
        'views/purchase_plan_view.xml',
        'views/purchase.xml',
        'views/mrp_production.xml',
        'views/res_company_view.xml',
        'views/purchase_order_view.xml',
        # 'reports/purchase_report_views.xml',
        # 'reports/purchase_plan.xml',
    ],
    'demo': [
    ],
}
