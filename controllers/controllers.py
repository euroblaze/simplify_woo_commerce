# -*- coding: utf-8 -*-
from odoo import http

class WooCreateOrders(http.Controller):

    @http.route('/api/create_order', auth='public', csrf=False, type='json', methods=['POST'])
    def create_product(self, **kwargs):
        print("====================================kwargs", kwargs)
        return "Hello World!"
        # new_product = http.request.env['product.template'].sudo().create(kwargs)
        # if new_product:
        #     return "New product has been created"
        # else:
        #     return "No product created"