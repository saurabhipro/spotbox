# -*- coding: utf-8 -*-
{
    'name': "spotboxai",
    'author': "SpotboxAI(Anjli Odoo Developer)",
    'category': 'spotboxai',
    'version': '0.1',
    'depends': ['base', 'account', 'sale', 'stock', 'hr'],
    'data': [
        'views/views.xml',
        'views/stock_picking_views.xml',
        'views/sale_order_views.xml',
        'views/hr_employee_views.xml',
    ],
}

