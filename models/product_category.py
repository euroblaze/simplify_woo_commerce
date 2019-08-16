# -*- coding: utf-8 -*-
from odoo import models, fields, api

#INHERT PRODUCT_CATEGORY AND ADD NEW FIELD FOR WOO_CHANNEL INSTANCE ID
class InhertProductCategory(models.Model):
    _inherit = 'product.category'

    woo_channel_id = fields.Many2one('channel.pos.settings', string='Channel Instance ID', description="Woo Channel instance ID")
    woo_category_id = fields.Integer(string='Woo Category ID')
    woo_parent_id = fields.Integer(string='Woo Category ID')


