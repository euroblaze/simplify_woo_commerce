# -*- coding: utf-8 -*-
from odoo import models, fields, api
from woocommerce import API
import datetime
import logging
_logger = logging.getLogger(__name__)

class InheritChannelPosSettingsWooCommerceConnector(models.Model):
    _inherit = 'channel.pos.settings'

    #pos field inherited and added id =3 for Woo Commerce Channel
    pos = fields.Selection(selection_add=[('3', 'Woo Commerce')])

    #Field for tax mapping
    woo_taxes_map = fields.One2many('woo.taxes.map', 'woo_channel_id', string="Taxes")
    woo_customers = fields.One2many('res.partner', 'woo_channel_id', string="Customers")

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
            # check the woo_commerce connection
            self.create_woo_commerce_object()
            # print(self.create_date)
            # print(type(self.create_date))
            logs = []
            logs.append((0, 0, {'date': str(datetime.datetime.now()), 'message': 'Connection Successful!! WC object created.',
                                'channel_id': self.id, 'type': 'CONFIG'}))
            self.update({'log_lines': logs})
        except Exception as e:
            _logger.error(e)

    # On button click import all taxes from Woo into woo.taxes table
    @api.one
    def import_woo_taxes(self):
        wcapi = self.create_woo_commerce_object()  # connect to Woo
        woo_taxes = wcapi.get("taxes").json()   # get all Woo taxes
        woo_taxes_obj = self.env['woo.taxes']

        # For every tax from woo taxes check if is created in woo.taxes table in odoo
        woo_tax_ids= []
        for tax in woo_taxes:

            print(tax)
            id = tax['id']
            woo_tax_ids.append(id)
            country = tax['country']
            state = tax['state']
            postcode = tax['postcode']
            city = tax['city']
            rate = tax['rate']
            name = tax['name']

            tax_exist = self.env['woo.taxes'].search_count([('woo_tax_id', '=', id)])
            if tax_exist == 1:  # First check if tax exist
                print("Tax already exist")
                # maybe the tax is updated in woo, so write the attributes again
                self.env['woo.taxes'].search([('woo_tax_id', '=', id)]).write({'country': country,
                                                                               'state': state,
                                                                               'postcode': postcode,
                                                                               'city': city,
                                                                               'rate': rate,
                                                                               'name': name,
                                                                               'channel_id': self.id})
                continue
            # If not exist then create the tax
            else:
                try:
                    is_created = woo_taxes_obj.create({'woo_tax_id': id, 'country': country, 'state': state,
                                                       'postcode': postcode, 'city': city, 'rate': rate, 'name': name,
                                                       'channel_id': self.id})
                    if is_created:
                        print("tax created")
                        logs = []
                        logs.append(
                            (0, 0, {'date': str(is_created.create_date), 'message': 'Woo tax ' + str(id) + ' successfully imported',
                                    'channel_id': self.id, 'type': 'Import tax'}))
                        self.update({'log_lines': logs})
                except Exception as e:
                    _logger.error(e)
        # Now in case of not first import into Odoo and some removed tax from woo
        # Delete from woo.taxes and woo.taxes.map the removed tax from woo

        woo_taxes_obj2 = self.env['woo.taxes'].search([('channel_id', '=', self.id)])
        for record in woo_taxes_obj2:
            if record.woo_tax_id not in woo_tax_ids:
                try:
                    self.env['woo.taxes.map'].search([('woo_tax', '=', record.id)]).unlink()
                    unlink = record.unlink()
                    if unlink:
                        logs = []
                        logs.append((0, 0,{'date': str(datetime.datetime.now()),
                                           'message': 'Woo tax ' + str(id) + ' has been deleted from Odoo',
                                           'channel_id': self.id, 'type': 'Delete tax'}))
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

    def check_deleted_customers(self, woo_customers_list):
        odoo_customers = self.env['res.partner'].search([('woo_channel_id', '=', self.id)])
        for customer in odoo_customers:
            if customer.woo_customer_id not in woo_customers_list:
                self.env['res.partner'].search([('woo_customer_id', '=', customer.woo_customer_id), ('woo_channel_id', '=', self.id)]).unlink()
                # log customer deleted
                logs = []
                logs.append(
                    (0, 0, {'date': str(self.create_date), 'message': 'Woo tax ' + str(id) + ' successfully imported',
                            'channel_id': self.id, 'type': 'Import tax'}))
                self.update({'log_lines': logs})

    def get_country_id(self, country_code):
        country_id = self.env['res.country'].search([('code', '=', country_code)]).id
        return country_id


    def parse_woo_customer_info(self, woo_customer):
        # INPUT - json format of woo customer
        # OUTPUT - 3 dictionaries with personal, billing and shipping information of the customer

        # personal information
        personal_info = {
            "woo_customer_id": woo_customer['id'],
            "email": woo_customer['email'],
            "name": woo_customer['first_name'] + " " + woo_customer['last_name'],
            # "role": woo_customer['role'],
            # "username": woo_customer['username'],
            "type": "contact",
            "woo_channel_id": self.id
        }

        # invoice/billing information
        billing_info = {}
        if woo_customer.get('billing'):
            billing_info = {
                "woo_customer_id": woo_customer['id'],
                "name": woo_customer['billing']['first_name'] + " " + woo_customer['billing']['last_name'],
                "company_name": woo_customer['billing']['company'],
                "street": woo_customer['billing']['address_1'],
                "street2": woo_customer['billing']['address_2'],
                "city": woo_customer['billing']['city'],
                "zip": woo_customer['billing']['postcode'],
                "country": self.get_country_id(woo_customer['billing']['country']),
                # "state": woo_customer['billing']['state'],
                "email": woo_customer['billing']['email'],
                "phone": woo_customer['billing']['phone'],
                "type": "invoice",
                "woo_channel_id": self.id
            }

        # shipping information
        shipping_info = {}
        if woo_customer.get('shipping'):
            shipping_info = {
                "woo_customer_id": woo_customer['id'],
                "name": woo_customer['shipping']['first_name'] + " " + woo_customer['shipping']['last_name'],
                "company_name": woo_customer['shipping']['company'],
                "street":  woo_customer['shipping']['address_1'],
                "street": woo_customer['shipping']['address_2'],
                "city": woo_customer['shipping']['city'],
                "zip": woo_customer['shipping']['postcode'],
                "country":self.get_country_id(woo_customer['shipping']['country']),
                # "state": woo_customer['shipping']['state'],
                "type": "delivery",
                "woo_channel_id": self.id

            }

        return personal_info, billing_info, shipping_info

    def is_updated(self, woo_customer_id, woo_channel_id, woo_date_modified):
        # INPUT:
        #     woo_customer_id in odoo
        #     woo_channel_id in odoo
        #     woo_date_modified : date of customer modification in Woo Commerce
        # OUTPUT: True or False, if there is need to update or not the customer in Odoo
        customer_records = self.env['res.partner'].search([('woo_customer_id', '=', woo_customer_id),
                                                           ('woo_channel_id', '=', woo_channel_id)])
        update = False
        print("======================")
        print(woo_date_modified)
        woo_date_modified = woo_date_modified.split("T")
        woo_date_modified = woo_date_modified[0] + " " + woo_date_modified[1]
        woo_date_modified = datetime.datetime.strptime(woo_date_modified, '%Y-%m-%d %H:%M:%S')
        for record in customer_records:
            odoo_modification_date = str(record.write_date).split(".")
            odoo_modification_date = datetime.datetime.strptime(odoo_modification_date[0], '%Y-%m-%d %H:%M:%S')
            if odoo_modification_date < woo_date_modified:
                print('Odoo modification date:')
                print(odoo_modification_date)
                print('Woo_date_modified: ')
                print(woo_date_modified)
                update = True
                break
        return update


    def import_woo_customers(self):
        print("Customers imported.")
        wcapi = self.create_woo_commerce_object()  # connect to Woo
        woo_customers = wcapi.get("customers").json()  # get all Woo customers
        # print(woo_customers)

        res_partner = self.env['res.partner']
        woo_customers_list = []

        for woo_customer in woo_customers:
            # print(woo_customer)
            woo_customers_list.append(woo_customer['id'])

            # first parse the customer info from woo
            personal_info, billing_info, shipping_info = self.parse_woo_customer_info(woo_customer)
            woo_id = personal_info['woo_customer_id']

            # next check if the master customer already exist in odoo
            # you will find the master customer with the woo_id and parent_id = null

            master_partner_exist = self.env['res.partner'].search_count([('woo_customer_id', '=', woo_id),
                                                                        ('woo_channel_id', '=', self.id)])
            print("Master partner 1:")
            print(woo_id)
            print(self.id)
            print(master_partner_exist)

            master_partner_exist = self.env['res.partner'].search_count([('woo_customer_id', '=', woo_id),
                                                                         ('woo_channel_id', '=', self.id),
                                                                         ('parent_id', '=', None)])
            print("Master partner 2: ")
            print(master_partner_exist)

            # if master customer exist
            if master_partner_exist == 1:
                print("Parent ID: ")

                print(master_partner_exist)

                # compare the time of updates and if needed make an update
                print("**************")
                print(woo_customer['date_modified'])

                woo_date_modified = woo_customer['date_modified']
                update = self.is_updated(woo_id, self.id, woo_date_modified)

                # get the master record ID
                parent = res_partner.search([('woo_customer_id', '=', woo_id),
                                             ('woo_channel_id', '=', self.id),
                                             ('parent_id', '=', None)], limit=1)
                parent_id = parent.id
                print(parent_id)

                # check if billing information exists
                if woo_customer['billing']['first_name'] != '':
                    #if billing information exists, next check if there is a billing record in res_partner
                    billing_record_exist = res_partner.search_count([('woo_customer_id', '=', woo_id),
                                                                     ('woo_channel_id', '=', self.id),
                                                                     ('parent_id', '=', parent_id),
                                                                     ('type', '=', 'invoice')])
                    # if billing record exist and woo_customer need to be updated then update the billing record
                    if billing_record_exist == 1 and update:
                        print('Billing record updated')
                        billing_record = res_partner.search([('woo_customer_id', '=', woo_id),
                                                             ('woo_channel_id', '=', self.id),
                                                             ('parent_id', '=', parent_id),
                                                             ('type', '=', 'invoice')]).write(billing_info)
                        print(res_partner.search([('woo_customer_id', '=', woo_id),
                                                             ('woo_channel_id', '=', self.id),
                                                             ('parent_id', '=', parent_id),
                                                             ('type', '=', 'invoice')]))
                        print(billing_record)

                    #if billing record does not exist  - create one
                    elif billing_record_exist == 0:
                        print("Billing record created")
                        billing_info.update({'parent_id': parent_id})
                        billing_record = res_partner.create(billing_info)
                        #log creation



                # check if shipping information exists i.e if at least first name exist
                if woo_customer['shipping']['first_name'] != '':
                    # if shipping information exists, next check if there is a shipping record in res_partner
                    shipping_record_exist = res_partner.search_count([('woo_customer_id', '=', woo_id),
                                                                     ('woo_channel_id', '=', self.id),
                                                                     ('parent_id', '=', parent_id),
                                                                     ('type','=', 'delivery')])
                    # if shipping record exist and woo_customer need to be updated then update the billing record
                    if shipping_record_exist == 1 and update:
                        print("Shipping record updated")
                        shipping_record = res_partner.search([('woo_customer_id', '=', woo_id),
                                                             ('woo_channel_id', '=', self.id),
                                                             ('parent_id', '=', parent_id),
                                                             ('type', '=', 'delivery')]).write(shipping_info)
                        print(shipping_record)

                    elif shipping_record_exist == 0:
                        print("Shipping record created")
                        shipping_info.update({'parent_id': parent_id})
                        shipping_record = res_partner.create(shipping_info)
                        # log creation

                # finally update the parent customer record
                parent.write(personal_info)
                #log update

            # if master customer does not exist
            else:
                # create master contact with type contact
                res_partner.create(personal_info)
                print("Parent customer created ")
                # log creation

                # get the master record ID
                parent_id = res_partner.search([('woo_customer_id', '=', woo_id),
                                                ('woo_channel_id', '=', self.id),
                                                ('parent_id', '=', None)], limit=1).id
                print(parent_id)

                # check if woo_customer has billing information
                if woo_customer['billing']['first_name'] != '':
                    print()
                    # if he has, then create child customer record with parent id
                    # billing_info.update({'parent_id': parent_id})
                    billing_info['parent_id'] = parent_id
                    billing_record = res_partner.create(billing_info)
                    print("Child customer record for billing information created")
                    # log creation


                # check if woo_customer has shipping information
                if woo_customer['shipping']['first_name'] != '':
                    # if it has, then create child customer record with parent id
                    # shipping_info.update({'parent_id': parent_id})

                    shipping_info['parent_id'] = parent_id
                    shipping_record = res_partner.create(shipping_info)
                    print("Child customer record created for shipping information created")
                    # log creation

        #After one or more importing check if there is some deleted customer in WooCommerce
        # If yes delete the customer from Odoo too.
        self.check_deleted_customers(woo_customers_list)

#write code for logs




















