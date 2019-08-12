# -*- coding: utf-8 -*-
from odoo import models, fields, api

#INHERT RES_PARTNER AND ADD NEW FIELD FOR WOO_CHANNEL INSTANCE ID
class InhertResPartner(models.Model):
    _inherit = 'res.partner'

    woo_channel_id = fields.Many2one('channel.pos.settings', string='Channel Instance ID', description="Woo Channel instance ID")
    woo_customer_id = fields.Integer(string='Woo Customer ID')
    # woo_role = fields.Selection([('-1', 'Please Select Role'),
    #                                          ('wc/v3', 'WC version 3.5.x or later'),
    #                                          ('wc/v2', 'WC version 3.0.x or later'),
    #                                          ('vc/v1', 'WC version 2.6.x or later'),
    #                                          ], string='Woo Commerce Version', default='-1')

