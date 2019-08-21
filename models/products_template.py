# -*- coding: utf-8 -*-
from odoo import models, fields, api

#INHERT PRODUCT_TEMPLATE AND ADD NEW FIELDS FOR WOO_CHANNEL INSTANCE ID
class InhertProductTemplate(models.Model):
    _inherit = 'product.template'

    # woo_channel_id = fields.Many2one('channel.pos.settings', string='Channel Instance ID', description="Woo Channel instance ID")
    woo_product_id = fields.Integer(string='Woo Product ID')
    woo_sale_price = fields.Float(string='Sale price', description="Price when the product is on sale")
    woo_regular_price = fields.Float(string='Regular price', description="Regular price of the product")







