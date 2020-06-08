# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductAttributeReMap(models.Model):
    _name = 'product.attribute.remap'

    original_value_id = fields.Many2one('product.attribute.value', string='Original Color', ondelete='restrict')
    remapped_value_ids = fields.Many2many('product.attribute.value', string='Remapped Values')
    channel_id = fields.Many2one('channel.pos.settings', string='Channel Instance ID',
                                     description="Woo Channel instance ID")
