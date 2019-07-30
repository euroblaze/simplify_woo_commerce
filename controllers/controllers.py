# -*- coding: utf-8 -*-
from odoo import http

# class CustomAddons/simplifyWooCommerce(http.Controller):
#     @http.route('/custom_addons/simplify_woo_commerce/custom_addons/simplify_woo_commerce/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_addons/simplify_woo_commerce/custom_addons/simplify_woo_commerce/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_addons/simplify_woo_commerce.listing', {
#             'root': '/custom_addons/simplify_woo_commerce/custom_addons/simplify_woo_commerce',
#             'objects': http.request.env['custom_addons/simplify_woo_commerce.custom_addons/simplify_woo_commerce'].search([]),
#         })

#     @http.route('/custom_addons/simplify_woo_commerce/custom_addons/simplify_woo_commerce/objects/<model("custom_addons/simplify_woo_commerce.custom_addons/simplify_woo_commerce"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_addons/simplify_woo_commerce.object', {
#             'object': obj
#         })