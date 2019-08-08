# -*- coding: utf-8 -*-
from odoo import models, fields, api
from woocommerce import API
import logging
_logger = logging.getLogger(__name__)

class InheritChannelPosSettingsWooCommerceConnector(models.Model):
    _inherit = 'channel.pos.settings'

    #pos field inherited and added id =3 for Woo Commerce Channel
    pos = fields.Selection(selection_add=[('3', 'Woo Commerce')])

    #Field for tax mapping
    woo_taxes_map = fields.One2many('woo.taxes.map', 'woo_channel_id', string="Taxes")

    #Fields for Woo Commerce configuration
    woo_host = fields.Char(string='Host')
    woo_username = fields.Char(string='Username')
    woo_password = fields.Char(string='Password')
    woo_consumer_key = fields.Char(string='Consumer Key')
    woo_consumer_secret = fields.Char(string='Consumer Secret')
    woo_commerce_version = fields.Selection([('-1', 'Please Select Version'),
                                             ('wc/v3', 'WC version 3.5.x or later'),
                                             ('wc/v2', 'WC version 3.0.x or later'),
                                             ('vc/v1', 'WC version 2.6.x or later'),
                                             ], string='Woo Commerce Version', default='-1')
    #Information fields for updates
    woo_last_update_product = fields.Datetime(string='Last product update', readonly=True)
    woo_last_update_order = fields.Datetime(string='Last order update', readonly=True)
    woo_last_update_customer = fields.Datetime(string='Last customer update', readonly=True)
    woo_last_update_tax = fields.Datetime(string='Last tax update', readonly=True)

    #Automation fields
    woo_interval_number = fields.Integer(string='Execute every')
    woo_interval_type = fields.Selection([('minutes', 'Minutes'),
                                           ('hours', 'Hours'),
                                           ('days', 'Days'),
                                           ('weeks', 'Weeks'),
                                           ('months', 'Months')], string='Interval Unit', default='hours')
    woo_nextcall = fields.Datetime(string='Next Execution Date', required=True, default=fields.Datetime.now, help="Next planned execution date for this job.")
    woo_cron_user_id = fields.Many2one('res.users')

    #Method for connection with Woo Commerce
    def create_woo_commerce_object(self):
        wcapi = API(
            url=self.woo_host,
            consumer_key=self.woo_consumer_key,
            consumer_secret=self.woo_consumer_secret,
            wp_api="wp-json",
            version=self.woo_commerce_version
        )
        print(wcapi)
        return wcapi
    @api.one
    def woo_test_connection(self):
        print("Connection Successful")
        try:
            #check the woo_commerce connection
            self.create_woo_commerce_object()
            # print(self.create_date)
            # print(type(self.create_date))
            logs = []
            logs.append((0, 0, {'date': str(self.create_date), 'message': 'Connection Successful!! WC object created.',
                                'channel_id': self.id, 'type': 'CONFIG'}))
            self.update({'log_lines': logs})
        except Exception as e:
            _logger.error(e)

    #On button click import all taxes from Woo into woo.taxes table
    @api.one
    def import_woo_taxes(self):
        wcapi = self.create_woo_commerce_object()  #connect to Woo
        woo_taxes = wcapi.get("taxes").json()   #get all Woo taxes
        woo_taxes_obj = self.env['woo.taxes']

        for tax in woo_taxes:
            print(tax)
            id = tax['id']
            country = tax['country']
            state = tax['state']
            postcode = tax['postcode']
            city = tax['city']
            rate = tax['rate']
            name = tax['name']

            tax_exist = self.env['woo.taxes'].search_count([('woo_tax_id', '=', id),
                                                      ('country', '=', country),
                                                      ('state', '=', state),
                                                      ('postcode', '=', postcode),
                                                      ('city', '=', city),
                                                      ('rate', '=', rate),
                                                      ('name', '=', name),
                                                      ('channel_id', '=', self.id)])
            if tax_exist == 1:  #First check if tax exist
                print("Tax already exist")
                continue
            else : #If not exist then create the tax
                try:
                    is_created = woo_taxes_obj.create({'woo_tax_id': id, 'country': country, 'state': state,
                                                       'postcode': postcode, 'city': city, 'rate': rate, 'name': name,
                                                       'channel_id': self.id})
                    if is_created:
                        logs = []
                        logs.append(
                            (0, 0, {'date': str(self.create_date), 'message': 'Woo tax ' + str(id) + ' successfully imported',
                                    'channel_id': self.id, 'type': 'Import tax'}))
                        self.update({'log_lines': logs})
                except Exception as e:
                    _logger.error(e)


    # @api.one
    # def map_woo_taxes(self):
    #     print("Tax mapped")
    #     view_id = self.env.ref('simplify_woo_commerce.woo_taxes_map').id
    #
    #     map_taxes = {
    #         'name': 'Map Woo Taxes',
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'views': [(view_id, 'form')],
    #         'view_id': view_id,
    #         'res_model': 'woo.taxes.map',
    #         'target': 'new',
    #         'context': {'default_woo_channel_id': self.id}
    #     }
    #     return map_taxes




