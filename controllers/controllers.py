# -*- coding: utf-8 -*-
from odoo import http
import logging
_logger = logging.getLogger(__name__)

class WooCreateOrders(http.Controller):

    @http.route('/api/create_order', auth='public', csrf=False, type='json', methods=['POST'])
    def create_order(self, **kwargs):
        _logger.info("===================================================WEBHOOK REQUEST ==================================================")
        _logger.info(http.request.jsonrequest)
        _logger.info("==========SELF=========")
        _logger.info(self)
        _logger.info("====================================================CREATE ORDER========================================================")
        new_order = http.request.env['channel.pos.settings'].sudo().import_woo_webhooks_orders([http.request.jsonrequest])

        return http.request.jsonrequest
        # new_product = http.request.env['product.template'].sudo().create(kwargs)
       
