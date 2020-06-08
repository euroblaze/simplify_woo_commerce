# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductAttributeReMap(models.Model):
    _name = 'product.attribute.remap'

    original_value_id = fields.Many2one('product.attribute.value', string='Original Value')
    remapped_value_ids = fields.Many2many('product.attribute.value', string='Remapped Values')
    product_tmpl_id = fields.Many2one('product.template', string='Product Template')

