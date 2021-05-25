# -*- coding: utf-8 -*-
from odoo import models, fields, api


class InhertProductAttribute(models.Model):
    _inherit = 'product.attribute'
    woo_attribute_id = fields.Integer(string='Woo Attribute ID')

class InhertProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    # @api.onchange('attribute_id')
    # def _onchange_attribute(self):
    #     # print(self._prefetch.get('product.attribute').pop())
    #     if self._prefetch.get('product.attribute'):
    #         return {
    #         'domain': {
    #             'value_parent_id': [('attribute_id', '=', self._prefetch.get('product.attribute').pop())]
    #         }}

    woo_attribute_value_id = fields.Integer(string='Woo Attribute Value ID')
    # value_parent_id = fields.Many2one('product.attribute.value', string="Parent Value")
