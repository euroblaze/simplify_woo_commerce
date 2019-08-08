# -*- coding: utf-8 -*-
from odoo import models, fields, api, http
from woocommerce import API
import json
import logging
_logger = logging.getLogger(__name__)


#CLASS FOR IMPORTING WOO COMMERCE TAXES
class ImportWooTaxes(models.Model):
    _name = 'woo.taxes'
    _description = 'Odoo <-> Woo Taxes Mapping'

    woo_tax_id = fields.Integer(string='Woo Tax ID')
    country = fields.Char(string='Country code')
    state = fields.Char(string='State code')
    postcode = fields.Char(string='Postcode / ZIP ')
    city = fields.Char(string='City')
    rate = fields.Float(string='Rate % ')
    name = fields.Char(string='Tax name')
    channel_id = fields.Many2one('channel.pos.settings', string='Channel')


#CLASS FOR MAPPING ODOO <-> WOO TAXES
class ChannelWooTaxes(models.Model):
    _name = 'woo.taxes.map'
    _description = 'Odoo <-> Woo Taxes Mapping'

    def _print_self(self, **kwargs):
        print(self._context.get('channel_id'))
        return self._context.get('channel_id')
        #Getting the channel_id from the url
        # dict = http.request.httprequest.__dict__
        # # for item in dict:
        # #     print(item)
        # cache = http.request.httprequest._cached_data.decode("utf-8").replace("'", '"')
        # print(cache)
        # data = json.loads(cache)
        # print(data['params']['kwargs']['context']['channel_id'])
        # id = data['params']['kwargs']['context']['channel_id']


    #set the domain for woo_tax to show just the taxes imported from the current woo instance
    @api.onchange('woo_channel_id')
    def _onchange_dul(self):
        return {
            'domain': {
                'woo_tax': [('channel_id', '=', self._context.get('channel_id'))]
            }}

    woo_tax = fields.Many2one('woo.taxes')
    odoo_tax = fields.Many2one('account.tax', string='Odoo mapped tax')
    woo_channel_id = fields.Many2one('channel.pos.settings', string='Channel', default=_print_self, readonly=True)

    @api.multi
    def create(self,vals):
        print(vals)
        result = super(ChannelWooTaxes, self).create(vals)
        return result





