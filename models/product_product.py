# -*- coding: utf-8 -*-
from odoo import models, fields, api

class OxidChannelProductProductInherit(models.Model):
    _inherit = 'product.product'

    woo_variant_id = fields.Char('Woo variant ID')
    woo_channel_id = fields.Many2one('channel.pos.settings', string='Channel Instance ID', description="Woo Channel instance ID")

