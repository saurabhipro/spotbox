# -*- coding: utf-8 -*-
{
    'name': "spotboxai",
    'author': "SpotboxAI(Anjli Odoo Developer)",
    'category': 'spotboxai',
    'version': '0.1',
    'depends': ['base', 'account', 'sale', 'stock', 'hr', 'auth_signup'],
    'data': [
        'security/hr_security.xml',
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'views/hr_employee_menu_views.xml',
        'views/views.xml',
        'views/stock_picking_views.xml',
        'views/sale_order_views.xml',
        'views/res_users_views.xml',
        'views/menu_views.xml',
    ],
}

