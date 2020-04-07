# -*- coding: utf-8 -*-
from odoo import http
import logging
_logger = logging.getLogger(__name__)

class WooCreateOrders(http.Controller):

    @http.route('/api/create_order', auth='public', csrf=False, type='json', methods=['POST'])
    def create_product(self, **kwargs):
        _logger.info("===================================================WEBHOOK REQUEST ==================================================")
        _logger.info(http.request.jsonrequest)
        _logger.info("============ID================")
        _logger.info(http.request.jsonrequest["id"])
        _logger.info("=========SELF=========")
        _loggwe.info(self)
        return "Hello World!"
        # new_product = http.request.env['product.template'].sudo().create(kwargs)
        # if new_product:
        #     return "New product has been created"
        # else:
        #     return "No product created"
