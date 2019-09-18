# -*- coding: utf-8 -*-
from odoo import models, fields, api

class InhertSaleOrder(models.Model):
    _inherit = 'sale.order'

    woo_order_number = fields.Integer(string='Woo Order Number')
    woo_order_key = fields.Char(string='Woo Order key')

