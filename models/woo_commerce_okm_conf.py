# -*- coding: utf-8 -*-
from odoo import models, fields, api
from woocommerce import API
import datetime
import logging
import requests
import base64

_logger = logging.getLogger(__name__)


class InheritChannelPosSettingsWooCommerceConnector(models.Model):
    _inherit = 'channel.pos.settings'

    # pos field inherited and added id =3 for Woo Commerce Channel
    pos = fields.Selection(selection_add=[('3', 'Woo Commerce')])

    # Field for tax mapping
    woo_taxes_map = fields.One2many('woo.taxes.map', 'woo_channel_id', string="Taxes")
    # Field for Customers
    woo_customers = fields.One2many('res.partner', 'woo_channel_id', string="Customers",
                                    domain=[('parent_id', '=', None)])
    # Field for categories
    woo_categories = fields.One2many('product.category', 'woo_channel_id',
                                     string="Product categories", )
    # Field for products
    woo_products = fields.One2many('product.template', 'channel_id', string="Products",
                                   domain=[('woo_product_id', '!=', None)])
    # Field for Sale Orders
    woo_orders = fields.One2many('sale.order', 'woo_channel_id', string="Sale Orders")


    # Fields for Woo Commerce configuration
    woo_host = fields.Char(string='Host')
    woo_username = fields.Char(string='Username')
    woo_password = fields.Char(string='Password')
    woo_consumer_key = fields.Char(string='Consumer Key')
    woo_consumer_secret = fields.Char(string='Consumer Secret')
    woo_commerce_version = fields.Selection([('-1', 'Please Select Version'),
                                             ('wc/v3', 'WC version 3.5.x or later'),
                                             ('wc/v2', 'WC version 3.0.x or later'),
                                             ('vc/v1', 'WC version 2.6.x or later'),
                                             ], string='Woo Commerce Version', default='wc/v3')
    # Information fields for updates
    woo_last_update_product = fields.Datetime(string='Last product update', readonly=True)
    woo_last_update_order = fields.Datetime(string='Last order update', readonly=True)
    woo_last_update_customer = fields.Datetime(string='Last customer update', readonly=True)
    woo_last_update_tax = fields.Datetime(string='Last tax update', readonly=True)

    # Automation fields
    woo_interval_number = fields.Integer(string='Execute every')
    woo_interval_type = fields.Selection([('minutes', 'Minutes'),
                                          ('hours', 'Hours'),
                                          ('days', 'Days'),
                                          ('weeks', 'Weeks'),
                                          ('months', 'Months')], string='Interval Unit', default='hours')
    woo_nextcall = fields.Datetime(string='Next Execution Date', required=True, default=fields.Datetime.now,
                                   help="Next planned execution date for this job.")
    woo_cron_user_id = fields.Many2one('res.users')

    # Method for connection with Woo Commerce
    def create_woo_commerce_object(self):
        wcapi = API(
            url=self.woo_host,
            consumer_key=self.woo_consumer_key,
            consumer_secret=self.woo_consumer_secret,
            wp_api="wp-json",
            version=self.woo_commerce_version if self.woo_commerce_version != '-1' else 'wc/v3',
            timeout=100
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
            logs.append(
                (0, 0, {'date': str(datetime.datetime.now()), 'message': 'Connection Successful!! WC object created.',
                        'channel_id': self.id, 'type': 'CONFIG'}))
            self.update({'log_lines': logs})
        except Exception as e:
            _logger.error(e)

    # On button click import all taxes from Woo into woo.taxes table
    @api.one
    def import_woo_taxes(self):
        wcapi = self.create_woo_commerce_object()  # connect to Woo
        page = 1
        woo_taxes = []
        # get all Woo taxes
        while True:
            taxes_per_page = wcapi.get('taxes', params={"per_page": 100, "page": page}).json()
            page += 1
            if not taxes_per_page:
                break
            woo_taxes += taxes_per_page
        woo_taxes_obj = self.env['woo.taxes']

        # For every tax from woo taxes check if is created in woo.taxes table in odoo
        woo_tax_ids = []
        # print("+++++++++++")
        # print(woo_taxes)
        for tax in woo_taxes:

            # print(tax)
            id = tax['id']
            woo_tax_ids.append(id)
            country = tax['country']
            state = tax['state']
            postcode = tax['postcode']
            city = tax['city']
            rate = tax['rate']
            name = tax['name']
            tax_class = tax['class']
            # print("TAX CLASSSSSSS", tax_class)

            tax_exist = self.env['woo.taxes'].search_count([('woo_tax_id', '=', id)])
            if tax_exist == 1:  # First check if tax exist
                # print("Tax already exist")
                # maybe the tax is updated in woo, so write the attributes again
                self.env['woo.taxes'].search([('woo_tax_id', '=', id)]).write({'country': country,
                                                                               'state': state,
                                                                               'postcode': postcode,
                                                                               'city': city,
                                                                               'rate': rate,
                                                                               'name': name,
                                                                               'channel_id': self.id,
                                                                               'tax_class': tax_class})
                continue
            # If not exist then create the tax
            else:
                try:
                    is_created = woo_taxes_obj.create({'woo_tax_id': id, 'country': country, 'state': state,
                                                       'postcode': postcode, 'city': city, 'rate': rate, 'name': name,
                                                       'channel_id': self.id,
                                                       'tax_class': tax_class})
                    if is_created:
                        # print("tax created")
                        logs = []
                        logs.append(
                            (0, 0, {'date': str(is_created.create_date),
                                    'message': 'Woo tax ' + str(id) + ' successfully imported',
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
                        logs.append((0, 0, {'date': str(datetime.datetime.now()),
                                            'message': 'Woo tax ' + str(id) + ' has been deleted from Odoo',
                                            'channel_id': self.id, 'type': 'Delete tax'}))
                        self.update({'log_lines': logs})
                except Exception as e:
                    _logger.error(e)

    def check_deleted_customers(self, woo_customers_list):
        odoo_customers = self.env['res.partner'].search([('woo_channel_id', '=', self.id)])
        for customer in odoo_customers:
            if customer.woo_customer_id not in woo_customers_list:
                # self.env['res.partner'].search(
                #     [('woo_customer_id', '=', customer.woo_customer_id), ('woo_channel_id', '=', self.id)]).unlink()
                customer.unlink()
                # log customer deleted
                logs = []
                logs.append(
                    (0, 0, {'date': str(self.create_date), 'message': 'Woo customer ' + str(id) + ' was deleted',
                            'channel_id': self.id, 'type': 'Delete customer'}))
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
                "street": woo_customer['shipping']['address_1'],
                "street": woo_customer['shipping']['address_2'],
                "city": woo_customer['shipping']['city'],
                "zip": woo_customer['shipping']['postcode'],
                "country": self.get_country_id(woo_customer['shipping']['country']),
                # "state": woo_customer['shipping']['state'],
                "type": "delivery",
                "woo_channel_id": self.id

            }

        return personal_info, billing_info, shipping_info

    def is_customer_updated(self, woo_customer_id, woo_channel_id, woo_date_modified):
        # INPUT:
        #     woo_customer_id in odoo
        #     woo_channel_id in odoo
        #     woo_date_modified : date of customer modification in Woo Commerce
        # OUTPUT: True or False, if there is need to update or not the customer in Odoo
        customer_records = self.env['res.partner'].search([('woo_customer_id', '=', woo_customer_id),
                                                           ('woo_channel_id', '=', woo_channel_id)])
        update = False
        woo_date_modified = woo_date_modified.split("T")
        woo_date_modified = woo_date_modified[0] + " " + woo_date_modified[1]
        woo_date_modified = datetime.datetime.strptime(woo_date_modified, '%Y-%m-%d %H:%M:%S')
        for record in customer_records:
            odoo_modification_date = str(record.write_date).split(".")
            odoo_modification_date = datetime.datetime.strptime(odoo_modification_date[0], '%Y-%m-%d %H:%M:%S')
            if odoo_modification_date < woo_date_modified:
                update = True
                break
        return update

    def import_woo_customers(self):
        wcapi = self.create_woo_commerce_object()  # connect to Woo
        page = 1
        woo_customers = []
        # get all Woo orders
        while True:
            customers_per_page = wcapi.get('customers', params={"per_page": 100, "page": page}).json()
            page += 1
            if not customers_per_page:
                break
            woo_customers += customers_per_page

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
                                                                         ('woo_channel_id', '=', self.id),
                                                                         ('parent_id', '=', None)])

            # if master customer exist
            if master_partner_exist == 1:

                # compare the time of updates and if needed make an update
                woo_date_modified = woo_customer['date_modified']
                if woo_date_modified is None:
                    update = False
                else:
                    update = self.is_customer_updated(woo_id, self.id, woo_date_modified)

                # get the master record ID
                parent = res_partner.search([('woo_customer_id', '=', woo_id),
                                             ('woo_channel_id', '=', self.id),
                                             ('parent_id', '=', None)], limit=1)
                parent_id = parent.id
                # print(parent_id)

                # check if billing information exists
                if woo_customer['billing']['first_name'] != '':
                    # if billing information exists, next check if there is a billing record in res_partner
                    billing_record_exist = res_partner.search_count([('woo_customer_id', '=', woo_id),
                                                                     ('woo_channel_id', '=', self.id),
                                                                     ('parent_id', '=', parent_id),
                                                                     ('type', '=', 'invoice')])
                    # if billing record exist and woo_customer need to be updated then update the billing record
                    if billing_record_exist == 1 and update:
                        # print('Billing record updated')
                        billing_record = res_partner.search([('woo_customer_id', '=', woo_id),
                                                             ('woo_channel_id', '=', self.id),
                                                             ('parent_id', '=', parent_id),
                                                             ('type', '=', 'invoice')]).write(billing_info)


                    # if billing record does not exist  - create one
                    elif billing_record_exist == 0:
                        try:
                            # print("Billing record created")
                            billing_info.update({'parent_id': parent_id})
                            billing_record = res_partner.create(billing_info)

                            # log creation
                            if billing_record:
                                logs = []
                                logs.append(
                                    (0, 0, {'date': str(billing_record.create_date),
                                            'message': 'Billing information imported for customer ' + str(
                                                billing_record.name),
                                            'channel_id': self.id, 'type': 'Customer import'}))
                                self.write({'log_lines': logs})
                        except Exception as e:
                            _logger.error(e)

                # check if shipping information exists i.e if at least first name exist
                if woo_customer['shipping']['first_name'] != '':
                    # if shipping information exists, next check if there is a shipping record in res_partner
                    shipping_record_exist = res_partner.search_count([('woo_customer_id', '=', woo_id),
                                                                      ('woo_channel_id', '=', self.id),
                                                                      ('parent_id', '=', parent_id),
                                                                      ('type', '=', 'delivery')])
                    # if shipping record exist and woo_customer need to be updated then update the billing record
                    if shipping_record_exist == 1 and update:
                        # print("Shipping record updated")
                        shipping_record = res_partner.search([('woo_customer_id', '=', woo_id),
                                                              ('woo_channel_id', '=', self.id),
                                                              ('parent_id', '=', parent_id),
                                                              ('type', '=', 'delivery')]).write(shipping_info)


                    elif shipping_record_exist == 0:
                        # print("Shipping record created")
                        try:
                            shipping_info.update({'parent_id': parent_id})
                            shipping_record = res_partner.create(shipping_info)
                            # log creation
                            if shipping_record:
                                logs = []
                                logs.append(
                                    (0, 0, {'date': str(shipping_record.create_date),
                                            'message': 'Shipping information imported for customer ' + str(
                                                shipping_record.name),
                                            'channel_id': self.id, 'type': 'Customer import'}))
                                self.write({'log_lines': logs})
                        except Exception as e:
                            _logger.error(e)

                # finally update the parent customer record
                try:
                    parent_update = parent.write(personal_info)
                    if parent_update:
                        logs = []
                        logs.append((0, 0, {'date': str(parent_update.write_date),
                                            'message': "Information updated for customer " + str(
                                                parent_update.name) + " with ID " + str(parent_id.woo_customer_id),
                                            'channel_id': self.id, 'type': 'Customer update'}))
                        self.write({'log_lines': logs})
                except Exception as e:
                    _logger.error(e)




            # if master customer does not exist
            else:
                # create master contact with type contact
                try:
                    customer_create = res_partner.create(personal_info)
                    # print("Parent customer created ")
                    # log creation
                    if customer_create:
                        logs = []
                        logs.append((0, 0, {'date': str(customer_create.create_date),
                                            'message': "Customer with ID " + str(
                                                customer_create.woo_commerce_id) + ' successfully imported',
                                            'channel_id': self.id, 'type': 'Customer import'}))
                        self.update({'log_lines': logs})
                except Exception as e:
                    _logger.error(e)

                # get the master record ID
                parent_id = res_partner.search([('woo_customer_id', '=', woo_id),
                                                ('woo_channel_id', '=', self.id),
                                                ('parent_id', '=', None)], limit=1).id
                # print(parent_id)

                # check if woo_customer has billing information
                if woo_customer['billing']['first_name'] != '':
                    # if he has, then create child customer record with parent id
                    # billing_info.update({'parent_id': parent_id})
                    billing_info['parent_id'] = parent_id
                    try:
                        res_partner.create(billing_info)

                    except Exception as e:
                        _logger.error(e)

                # check if woo_customer has shipping information
                if woo_customer['shipping']['first_name'] != '':
                    # if it has, then create child customer record with parent id
                    # log creation
                    try:
                        shipping_info['parent_id'] = parent_id
                        res_partner.create(shipping_info)
                        # print("Child customer record created for shipping information")
                    except Exception as e:
                        _logger.error(e)

        # After one or more importing check if there is some deleted customer in WooCommerce
        # If yes delete the customer from Odoo too.
        self.check_deleted_customers(woo_customers_list)

    def import_woo_categories(self, woo_categories):
        # INPUT - json format of Woo categories
        # OUTPUT - importing this categories into Odoo product.category
        woo_categories.sort(key=lambda s: s['parent'])
        # print(woo_categories)
        for category in woo_categories:
            # print(category)
            duplicate_category = self.env['product.category'].search_count([('woo_category_id', '=', category['id']),('woo_channel_id', '=', self.id)])
            # print('DUPLICATE CATEGORY', duplicate_category)
            if duplicate_category != 0:
                odoo_category = self.env['product.category'].search([('woo_category_id', '=', category['id']),('woo_channel_id', '=', self.id)])
                # print('ODOO CATEGORY', odoo_category)
                odoo_category.write({
                    'woo_parent_id': category['parent'],
                    'name': category['name'],
                    'woo_channel_id': self.id,
                })
                woo_parent = odoo_category['woo_parent_id']
                # print("WOO PARENT", woo_parent)
                if woo_parent != 0:
                    parent_category = self.env['product.category'].search([('woo_category_id', '=', woo_parent),
                                                                           ('woo_channel_id', '=', self.id)
                                                                           ],
                                                                          limit=1)

                    # print("CATEGORY PARENT 1", parent_category)
                    odoo_category.write({
                        'parent_id': parent_category.id
                    })

            else:
                odoo_category = self.env['product.category'].create({
                    'woo_category_id': category['id'],
                    # 'parent_id' : category['parent'],
                    'woo_parent_id': category['parent'],
                    'name': category['name'],
                    'woo_channel_id': self.id,
                })
                woo_parent = odoo_category['woo_parent_id']
                # print("WOO PARENT", woo_parent)
                if woo_parent != 0:
                    parent_category = self.env['product.category'].search([('woo_category_id', '=', woo_parent),
                                                                           ('woo_channel_id', '=', self.id)
                                                                           ],
                                                                          limit=1)

                   # print("CATEGORY PARENT 1", parent_category)
                    odoo_category.write({
                        'parent_id': parent_category.id
                    })

    def get_current_product_price(self, woo_product):
        sale_price = woo_product['sale_price']  # Sale price in woo
        sales_price = woo_product['regular_price']  # Current product in Odoo

        if sale_price == '':  # check if the product is on sale
            print("THE PRODUCT IS NOT ON SALE!!!")
            sales_price = woo_product['regular_price']

        else:  # if the product is on sale
            date_now = str(datetime.datetime.now()).split(".")  # to igonre miliseconds
            date_now = datetime.datetime.strptime(date_now[0], '%Y-%m-%d %H:%M:%S')
            date_on_sale_from = woo_product['date_on_sale_from']

            # check if date_on_sale_from is scheduled
            if date_on_sale_from is not None:
                date_on_sale_from = date_on_sale_from.split("T")
                date_on_sale_from = date_on_sale_from[0] + ' ' + date_on_sale_from[1]
                date_on_sale_from = datetime.datetime.strptime(date_on_sale_from, '%Y-%m-%d %H:%M:%S')

                date_on_sale_to = woo_product['date_on_sale_to']
                if date_on_sale_to is not None:  # check if date_on_sale_to is scheduled
                    date_on_sale_to = woo_product['date_on_sale_to'].split("T")
                    date_on_sale_to = date_on_sale_to[0] + ' ' + date_on_sale_to[1]
                    date_on_sale_to = datetime.datetime.strptime(date_on_sale_to, '%Y-%m-%d %H:%M:%S')

                    if date_on_sale_from <= date_now and date_now <= date_on_sale_to:
                        print('PRODUCT ON SALE!!!')
                        sales_price = sale_price
                else:  # if date_on_sale_to is not scheduled
                    if date_on_sale_from <= date_now:
                        sales_price = sale_price
        return sales_price

    def create_woo_attributes_and_values(self, woo_variant):
        attr_id = ''
        list_vals = []
        attr_and_vals = {}
        attribute_obj = self.env['product.attribute']
        value_obj = self.env['product.attribute.value']

        # get all attributes from the product variant
        attributes = woo_variant['attributes']
        for attribute in attributes:
            attr_id = ''
            list_vals = []
            # print("Variant attribute", attribute)
            # get attribute name and value
            attr_name = attribute['name']
            attr_value = attribute['option']
            # odoo_attr_names = [attr.name.lower() for atrr in attribute_obj.search([])]
            odoo_attr_names_and_ids = {}

            # get all attributes names and their ids from Odoo
            for attr in attribute_obj.search([]):
                # print("Odoo ATTR", attr)
                name = attr.name.lower()
                id = attr.id
                odoo_attr_names_and_ids[name] = id
                # print("Odoo attr names and IDS", odoo_attr_names_and_ids)

            # check if the attribute exist in Odoo
            # print("Attribute exist in Odoo", attr_name.lower() in odoo_attr_names_and_ids.keys())
            if attr_name.lower() in odoo_attr_names_and_ids.keys():
                # attribute already exist
                attr_id = odoo_attr_names_and_ids[attr_name.lower()]
                # print('Attribute exiat with ID ', attr_id)
                # check if value exist
                value_exist = value_obj.search([('name', '=', attr_value), ('attribute_id', '=', attr_id)])

                # if value does not exist => create the value
                if value_exist:
                    # print("Value exist")
                    list_vals.append(value_exist.id)
                else:
                    # print("Value does not exist")
                    create_value = value_obj.create({'name': attr_value,
                                                     'attribute_id': attr_id})
                    # print("Created value", create_value)
                    list_vals.append(create_value.id)
            else:  # attribute does not exist => create attribute
                attribute_create = attribute_obj.create({'name': attr_name})
                # print("Attribute create", attribute_create)
                attr_id = attribute_create.id
                # create value
                create_value = value_obj.create({'name': attr_value,
                                                 'attribute_id': attr_id})
                # print("Created value", create_value)
                list_vals.append(create_value.id)

            attr_and_vals[attr_id] = list_vals
        return attr_and_vals

    def get_woo_product_images(self, woo_product, product_tmpl_id):
        aRelValues = {}

        # check if the product has images
        images = woo_product['images']
        product_image_ids = []
        # if images exists
        if images:
            # list with image ids for the odoo product
            product_image_ids = []
            image_id = 1
            for image in images:

                # this is image medium (display image of the product)
                if image_id == 1:
                    image_id = image_id + 1
                    image_response = requests.get(image['src'], stream=True, verify=False, timeout=10)
                    if image_response.status_code == 200:
                        image_binary = base64.b64encode(image_response.content)
                        aRelValues['image_medium'] = image_binary

                # images from the gallery
                else:
                    image_response = requests.get(image['src'], stream=True, verify=False, timeout=10)
                    if image_response.status_code == 200:
                        image_binary = base64.b64encode(image_response.content)
                        # add the image into product image
                        wooCreateImage = self.env['product.image'].create({
                            'name': image['name'],
                            'woo_image_id': image['id'],
                            'woo_channel_id': self.id,
                            'image': image_binary,
                            'product_tmpl_id': product_tmpl_id
                        })
                        product_image_ids.append(wooCreateImage.id)
        # add the images to the master product
        aRelValues['product_image_ids'] = [(6, 0, product_image_ids)]

        return aRelValues

    def check_deleted_products(self, woo_products_list):
        odoo_products = self.env['product.template'].search([('channel_id', '=', self.id),
                                                             ('woo_product_id', '!=', None),
                                                             ('master_id', '!=', None)])
        for product in odoo_products:
            if product.woo_product_id not in woo_products_list:
                product.active = False
                # log customer deleted
                logs = []
                logs.append(
                    (0, 0, {'date': str(self.create_date), 'message': 'Woo product ' + str(id) + ' was deleted',
                            'channel_id': self.id, 'type': 'Delete product'}))
                self.update({'log_lines': logs})

    def get_woo_product_variants(self, woo_product, wcapi, odoo_product):
        stock_quant = self.env['stock.quant']
        sku = woo_product['sku']  # Stock keeping unit, should be unique - something like isbn on the books
        product_product = self.env['product.product']

        if woo_product.get('variations') != []:
            # print('===============================================')
            product_id = woo_product['id']
            variations = wcapi.get('products/' + str(product_id) + '/variations').json()
            # print("VARIATIONS", variations)
            all_attrs_and_vals = {}
            # lista od listi so vrednosti na varijantite
            woo_variant_vals = []
            for variation in variations:
                # if the product has variants
                # Atributi i vrednosti za site varijanti na proizvodot. primer Boja i site vrednosti za boja. Golemina i site golemini.
                attr_and_vals = self.create_woo_attributes_and_values(variation)

                # print("ATTR_AND_VALS: ", attr_and_vals)
                tmp_list = []
                for attr_id in attr_and_vals.keys():
                    vals = attr_and_vals[attr_id]
                    vals.sort()
                    # print("VALS ", vals)
                    tmp_list += vals
                    # print("Woo WALS", woo_variant_vals)
                    if attr_id in all_attrs_and_vals:
                        all_attrs_and_vals[attr_id] += vals
                    else:
                        all_attrs_and_vals[attr_id] = vals
                # print("TMP Vals", tmp_list)
                woo_variant_vals.append(tmp_list)
                # print("Woo variant val", woo_variant_vals)
            list_all = []
            for key in all_attrs_and_vals.keys():
                # print("Key ", key)
                # print("Values", all_attrs_and_vals[key])
                list_val = all_attrs_and_vals[key]
                # first check if already exist product.template-attribute.line for this attribute and product
                ptal_exist = self.env['product.template.attribute.line'].search_count(
                    [('product_tmpl_id', '=', odoo_product.id),
                     ('attribute_id', '=', key)])
                p_tmpl_a_line = []
                if ptal_exist !=0 :
                    p_tmpl_a_line = self.env['product.template.attribute.line'].search(
                        [('product_tmpl_id', '=', odoo_product.id),
                         ('attribute_id', '=', key)])
                    p_tmpl_a_line.write({'value_ids': [(6, 0, list_val)]})
                else:
                    p_tmpl_a_line = self.env['product.template.attribute.line'].create(
                        {'product_tmpl_id': odoo_product.id,
                         'attribute_id': key,
                         'value_ids': [(6, 0, list_val)]})
                # print("PRODUCT TEMPLATE ATTRIBUTE LINE", p_tmpl_a_line)
                list_all.append(p_tmpl_a_line.id)
                # print("List ALL", list_all)

            # for the product create attribute_line_ids -> automatically product variants are being created
            prod_prods = odoo_product.write({'attribute_line_ids': [(6, 0, list_all)]})
            # print("Product_product", prod_prods)
            # get the corresponding variants for the product
            corresponding_product_variants = product_product.search(
                [('product_tmpl_id', '=', odoo_product.id)])
            # print("Coresponding product variants:", corresponding_product_variants)
            location = self.env['stock.location'].search([('name', '=', 'Stock'),
                                                          ('location_id', '!=', None)], limit=1)

            for odoo_variant in corresponding_product_variants:
                # print("Odoo variant attrs lines: ", odoo_variant.attribute_value_ids )
                value_ids = [value.id for value in odoo_variant.attribute_value_ids]
                # print("VALUE IDS", value_ids)
                # print("WOO WARIANT VALS", woo_variant_vals)
                # print("Odoo Variant in Woo variants1", value_ids in woo_variant_vals)
                if value_ids not in woo_variant_vals:
                    odoo_variant.unlink()
                    pass

                else:
                    index = woo_variant_vals.index(value_ids)
                    woo_variant = variations[index]
                    # print("Woo variant", woo_variant)
                    status = True if woo_variant['status'] == 'publish' else False
                    # print('Variant price', woo_variant['price'])
                    odoo_variant.write({'woo_variant_id': woo_variant['id'],
                                        'default_code': sku,
                                        'active': status,
                                        'type': 'product',
                                        'price': float(woo_variant['price']),
                                        'lst_price': float(woo_variant['price']),
                                        'list_price': float(woo_variant['price']),
                                        'price_extra': abs(
                                            float(woo_product['price']) - float(woo_variant['price'])),
                                        'woo_price': float(woo_variant['price']),
                                        'woo_channel_id': self.id})
                    # print('Variant list price', odoo_variant.lst_price)
                    image_medium = woo_variant['image']
                    if image_medium:
                        image_response = requests.get(image_medium['src'], stream=True, verify=False,
                                                      timeout=10)
                        if image_response.status_code == 200:
                            image_binary = base64.b64encode(image_response.content)
                            odoo_variant.write({'image_medium': image_binary})
                    variant_stock = woo_variant['stock_quantity']
                    # print("VARIANT QUANTITY", variant_stock)
                    if variant_stock is None:
                        variant_stock = 0
                    stock_exist = stock_quant.search_count([('product_id', '=', odoo_variant.id), ('location_id', '=', location.id)])
                    if stock_exist != 0:
                        stock = stock_quant.search([('product_id', '=', odoo_variant.id), ('location_id', '=', location.id)])
                        # print("STOCK=======", stock)
                        stock.write({'quantity': float(variant_stock)})
                    else:
                        stock = stock_quant._update_available_quantity(odoo_variant, location, float(variant_stock))

    def find_category(self, woo_category_id):
        category = self.env['product.category'].search([('woo_category_id', '=', woo_category_id),
                                                        ('woo_channel_id', '=', self.id)])
        return category.id

    def check_woo_product_update(self, woo_date_modified, odoo_date_modified):
        update = False
        woo_date_modified = woo_date_modified.split("T")
        woo_date_modified = woo_date_modified[0] + " " + woo_date_modified[1]
        woo_date_modified = datetime.datetime.strptime(woo_date_modified, '%Y-%m-%d %H:%M:%S')
        odoo_date_modified = str(odoo_date_modified).split(".")
        odoo_date_modified = datetime.datetime.strptime(odoo_date_modified[0], '%Y-%m-%d %H:%M:%S')
        if odoo_date_modified < woo_date_modified:
            update = True
        return update

    def import_woo_products(self):
        # print("Products import")
        wcapi = self.create_woo_commerce_object()  # connect to Woo
        page = 1
        woo_products = []
        # get all Woo products
        while True:
            products_per_page = wcapi.get('products', params={"per_page": 100, "page": page}).json()
            page += 1
            if not products_per_page:
                break
            woo_products += products_per_page

        woo_categories = []
        #get all woo categories
        page = 1
        while True:
            categories_per_page = wcapi.get('products/categories', params={"per_page": 100, "page": page}).json()
            page += 1
            if not products_per_page:
                break
            woo_categories += products_per_page

        woo_product_list = []

        # before product import, import all categories
        # print("=========================== CATEGORIES =================================================")
        self.import_woo_categories(woo_categories)

        # print("=========================== PRODUCTS =================================================")
        attribute_obj = self.env['product.attribute']
        value_obj = self.env['product.attribute.value']
        product_template = self.env['product.template']
        product_product = self.env['product.product']
        stock_quant = self.env['stock.quant']
        stock_change_product_qty = self.env['stock.change.product.qty']

        for woo_product in woo_products:
            print(woo_product)

            aRelValues = {}
            woo_id = woo_product['id']
            woo_product_list.append(woo_id)
            sku = woo_product['sku']  # Stock keeping unit, should be unique - something like isbn on the books
            # check if product exist - search with sku number
            master_product_exists = product_template.search([('default_code', '=', sku), ('master_id', '=', None)],
                                                            limit=1)
            # print("Master product exist: ", master_product_exists)

            product_categories = woo_product['categories']
            woo_category_id = product_categories[0]['id']
            # parse the product basic info
            woo_product_info = {
                'name': woo_product['name'],
                'type': 'product',
                'active': True if woo_product['status'] == 'publish' else False,
                # active da zavisi od Woo status or woo catalog_visibility
                'description': woo_product['description'],
                'woo_regular_price': woo_product['price'],  # regular price
                'woo_sale_price': woo_product['sale_price'],  # price on sale
                'price': woo_product['price'],  # current price
                'default_code': str(sku),
                'woo_sku': sku,


            }
            # print("PRODUCT PRICE", woo_product['price'])
            # print("DICT1", woo_product_info)
            # check if the product has tax
            tax_class = woo_product['tax_class']
            # print("TAX CLASS", tax_class)
            if tax_class == '':
                tax_class = 'standard'
            # print("TAX CLASS", tax_class)
            odoo_taxes = [tax.odoo_tax.id for tax in self.woo_taxes_map if tax.woo_tax.tax_class == tax_class]



            # if master product exist create/update the clone product for Woo Commerce
            if master_product_exists:
                # print("Master product exist")
                master_id = master_product_exists.id
                # print(master_product_exists.taxes_id)
                # print(master_id)
                # if master exist check if clone exist
                clone_exist =self.env['product.template'].search_count([('default_code', '=', sku),
                                                                        ('master_id', '=', master_id),
                                                                        ('channel_id', '=', self.id)])

                if clone_exist:
                    #if clone exist => update clone information
                    woo_clone = self.env['product.template'].search([('default_code', '=', sku),
                                                                 ('master_id', '=', master_id),
                                                                 ('channel_id', '=', self.id)])
                    # check if product need to be updated
                    woo_date_modified = woo_product['date_modified']
                    odoo_date_modified = woo_clone.write_date
                    update = self.check_woo_product_update(woo_date_modified, odoo_date_modified)
                    if update:
                        # update product images (if exist)
                        clone_woo_id = woo_clone.id
                        aRelValues = self.get_woo_product_images(woo_product, clone_woo_id)
                        woo_clone.write(aRelValues)
                        #update product category
                        woo_clone.write({
                            'categ_id': self.find_category(woo_category_id)
                        })
                        # update product variants (if exist)
                        self.get_woo_product_variants(woo_product, wcapi, woo_clone)
                        # print('Odoo taxes', odoo_taxes)
                        woo_clone.write({'taxes_id': [(6, 0, odoo_taxes)]})
                        woo_clone.write({'weight': woo_product['weight'] if woo_product['weight'] else 0})
                        # print("DICT2", woo_product_info)
                else:
                    #if clone does not exist => create woo clone
                    woo_product_info.update({
                        'woo_product_id': woo_product['id'],
                        'channel_id': self.id,
                        'master_id': master_id,
                        'categ_id': self.find_category(woo_category_id)
                    })
                    # print("DICT4", woo_product_info)
                    # print(woo_product_info['message_follower_ids'])
                    if woo_product_info.get('message_follower_ids'):
                        del woo_product_info['message_follower_ids']
                    # print("DICT", woo_product_info)
                    woo_clone = self.env['product.template'].create(woo_product_info)
                    clone_woo_id = woo_clone.id

                    # set images to the clone if the product has images
                    aRelValues = self.get_woo_product_images(woo_product, clone_woo_id)
                    woo_clone.write(aRelValues)

                    # Add variants to the clone if the product has variants
                    self.get_woo_product_variants(woo_product, wcapi, woo_clone)
                    woo_clone.write({'taxes_id': [(6, 0, odoo_taxes)]})
                    woo_clone.write({'weight': woo_product['weight'] if woo_product['weight'] else 0})
            # master product does not exist -> create master product and clone
            else:
                # create master product
                master_product = self.env['product.template'].create(woo_product_info)
                # print("DICT3", woo_product_info)
                master_id = master_product.id

                # get product images if it has
                aRelValues = self.get_woo_product_images(woo_product, master_id)
                master_product.write(aRelValues)

                # check from product variants
                self.get_woo_product_variants(woo_product, wcapi, master_product)
                # if does not have variants check if has attribute

                # create duplicate product for Woo commerce =====================================================
                woo_product_info.update({
                    'woo_product_id': woo_product['id'],
                    'channel_id': self.id,
                    'master_id': master_id,
                    'categ_id': self.find_category(woo_category_id)
                })
                # print("DICT4", woo_product_info)
                # print(woo_product_info['message_follower_ids'])
                if woo_product_info.get('message_follower_ids'):
                    del woo_product_info['message_follower_ids']
                # print("DICT", woo_product_info)
                woo_clone = self.env['product.template'].create(woo_product_info)
                clone_woo_id = woo_clone.id

                # set images to the clone if the product has images
                aRelValues = self.get_woo_product_images(woo_product, clone_woo_id)
                woo_clone.write(aRelValues)

                # Add variants to the clone if the product has variants
                self.get_woo_product_variants(woo_product, wcapi, woo_clone)
                woo_clone.write({'taxes_id': [(6, 0, odoo_taxes)]})
                woo_clone.write({'weight': woo_product['weight'] if woo_product['weight'] else 0})
                # print("DICT2", woo_product_info)

        # check for deleted products in Woo, If some product is deleted in Woo -> delete the product in Odoo too
        self.check_deleted_products(woo_product_list)

    def create_woo_order_lines(self, order_lines):

        for line in order_lines:

            product_id = line['product_id']
            print("PRODUCT ID", product_id)

            product = self.env['product.template'].search([('woo_product_id', '=', product_id),
                                                           ('master_id', '!=', None),
                                                           ('channel_id', '=', self.id)])
            print("PRODUCT _LINE", product)

            if line['variation_id']:
                variant = self.env['product.product'].search([('woo_variant_id', '=', line['variation_id']),
                                                              ('woo_channel_id', '=', self.id),
                                                              ('product_tmpl_id', '=', product.id)])
                print("Variant", variant)



    def import_woo_orders(self):
        wcapi = self.create_woo_commerce_object()  # connect to Woo
        page = 1
        woo_orders = []
        # get all Woo orders
        while True:
            orders_per_page = wcapi.get('orders', params={"per_page": 100, "page": page}).json()
            page += 1
            if not orders_per_page:
                break
            woo_orders += orders_per_page

        for order in woo_orders:
            print(order)
            woo_order_number = order['number']
            woo_order_key = order['order_key']
            partner_id = self.env['res.partner'].search([('woo_customer_id', '=', order['customer_id']),
                                                         ('woo_channel_id', '=', self.id),
                                                         ('parent_id', '=', None)])
            sale_order_info = {
                'woo_channel_id': self.id,
                'woo_order_number': woo_order_number,
                'woo_order_key': woo_order_key,
                'partner_id': partner_id.id,

             }
            print("SALE ORDER INFO", sale_order_info)

            order_exists = self.env['sale.order'].search_count([('woo_channel_id', '=', self.id),
                                                                ('woo_order_number', '=', woo_order_number),
                                                                ('woo_order_key', '=', woo_order_key)])
            order_lines = order['line_items']


            if order_exists != 0:
                #order exist => check if the order need to be updated
                print("Order already exist")
                sale_order = self.env['sale.order'].search([('woo_channel_id', '=', self.id),
                                                            ('woo_order_number', '=', woo_order_number),
                                                            ('woo_order_key', '=', woo_order_key)])
            else: #create order
                print("Create order")

                self.create_woo_order_lines(order_lines)