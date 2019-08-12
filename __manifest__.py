# -*- coding: utf-8 -*-
{
    'name': "simplify_woo_commerce",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "simplify-erp",
    'website': "http://www.simplify-erp.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'simplify_okm_core','sale_management','account','stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/woo_taxes.xml',
        'views/woo_commerce_conf.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}