# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools import float_compare, pycompat


class WooChannelProductProductInherit(models.Model):
    _inherit = 'product.product'

    woo_variant_id = fields.Char('Woo variant ID')
    woo_channel_id = fields.Many2one('channel.pos.settings', string='Channel Instance ID',
                                     description="Woo Channel instance ID")
    lst_price = fields.Float(
        'Sale Price', compute='_compute_product_lst_price',
        help="The sale price is managed from the product template. Click on the 'Configure Variants' button to set the extra attribute prices.")
    woo_price = fields.Float('Sale Price')

    @api.depends('list_price', 'price_extra')
    def _compute_product_lst_price(self):
        to_uom = None
        if 'uom' in self._context:
            to_uom = self.env['uom.uom'].browse([self._context['uom']])

        for product in self:
            if product.woo_channel_id is not None:
                product.lst_price = product.woo_price
                # print("Compute product lst_price", product.lst_price)
                product.list_price = product.woo_price
                # print("Compute product list_price", product.list_price)
            else:
                if to_uom:
                    list_price = product.uom_id._compute_price(product.list_price, to_uom)
                else:
                    list_price = product.list_price
                product.lst_price = list_price + product.price_extra





