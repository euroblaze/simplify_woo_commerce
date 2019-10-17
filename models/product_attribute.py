# -*- coding: utf-8 -*-
from odoo import models, fields, api


class InhertProductAttribute(models.Model):
    _inherit = 'product.attribute'

    woo_attribute_id = fields.Integer(string='Woo Attribute ID')

class InhertProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    woo_attribute_value_id = fields.Integer(string='Woo Attribute Value ID')