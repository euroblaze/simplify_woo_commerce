# -*- coding: utf-8 -*-
from odoo import models, fields, api


class InhertProductAttribute(models.Model):
    _inherit = 'product.attribute'

    woo_attribute_id = fields.Integer(string='Woo Attribute ID')