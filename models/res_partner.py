# -*- coding: utf-8 -*-
from odoo import models, fields, api

#INHERT RES_PARTNER AND ADD NEW FIELD FOR WOO_CHANNEL INSTANCE ID
class InhertResPartner(models.Model):
    _inherit = 'res.partner'

    woo_channel_id = fields.Many2one('channel.pos.settings', string='Channel Instance ID', description="Woo Channel instance ID")
    woo_customer_id = fields.Integer(string='Woo Customer ID')


