# -*- coding: utf-8 -*-
from odoo import models, fields

#INHERT PRODUCT_IMAGE AND ADD NEW FIELDS FOR WOO_CHANNEL INSTANCE ID AND WOO IMAGE ID
class InheritProductImage(models.Model):
    _inherit = 'product.catalog.image'

    woo_image_id = fields.Integer(string="Woo Image ID")
    woo_channel_id = fields.Many2one('channel.pos.settings', string='Channel Instance ID',
                                     description="Woo Channel instance ID")

