# Introduction

The odoo-Woo Commerce Connector is part of the SimplifyERP Multi channel module (OKM).  The purpose of this module is connecting any Woo Commerce Shop with Odoo. 

This connector is created for  Odoo 12 Community version using Python 3.6.
The main functionalities of this connector are :

- Connect with Woo Commerce Shop
- Import / Update Taxes
- Import / Update  Customers
- Import / Update Products
- Export Products
- Import / Update Orders
- Scheduling
- Log information

All of this functionalities will be explained in details in the following sections. 

# Woo Commerce OKM Configuration

## Class Description

Simplify Woo Commerce module `_inhert`  the `'channel.pos.settings'` class from the `simplify_okm_core` module.
In the inherited class are added additional fields needed for the connector to work.  
All fields and methods in this class are explained in the text bellow. 

### OKM Fields

The field `pos` from the `'channel.pos.settings'` class is extended and added new  `selection` in it  with ID for Woo Commerce. 

    pos = fields.Selection(selection_add=[('3', 'Woo Commerce')])

This field serve as a flag to show fields and tabs for the Woo Commerce Connector.

### API Configuration Fields

Additionally are added fields for *Woo commerce API Configuration . 
*****This fields are used for creating connection with the Woo Commerce Shop. 

        woo_host = fields.Char(string='Host')
        woo_username = fields.Char(string='Username')
        woo_password = fields.Char(string='Password')
        woo_consumer_key = fields.Char(string='Consumer Key')
        woo_consumer_secret = fields.Char(string='Consumer Secret')
        woo_commerce_version = fields.Selection([('-1', 'Please Select Version'),
                                                 ('wc/v3', 'WC version 3.5.x or later'),
                                                 ('wc/v2', 'WC version 3.0.x or later'),
                                                 ('vc/v1', 'WC version 2.6.x or later'),
                                                 ], string='Woo Commerce Version', default='-1', required=True)

The main control panel of the connector is available in the Settings section with a Menu appropriately named as Multichannel (see OKM menu). 
The API Configuration tab design is shown in the *Picture 1* . 

The credentials required for API configuration can be generated in the Woo Shop.

 **

[](https://www.notion.so/a96e0db1389e411fbf041b5c4ab6d42b#407f2ff1eb6c400599bf8f5737349975)

  *Picture 1. Woo Commerce API Configuration tab* 

                                                         

### Automation fields

We use automation fields in order to set up the `crone`  for future automatic data import from Woo Commerce Shop into Odoo.  

        woo_interval_number = fields.Integer(string='Execute every')
        woo_interval_type = fields.Selection([('minutes', 'Minutes'),
                                              ('hours', 'Hours'),
                                              ('days', 'Days'),
                                              ('weeks', 'Weeks'),
                                              ('months', 'Months')], string='Interval Unit', default='hours')
        woo_nextcall = fields.Datetime(string='Next Execution Date', required=True, default=fields.Datetime.now,
                                       help="Next planned execution date for this job.")
        woo_cron_user_id = fields.Many2one('res.users') 

Automation fields are shown in the Scheduling tab of the connector's Control Panel. 
 *Picture 2* shows the Scheduling tab. 

The crone is called with the method `import_woo_data` . 
The function of this method is just to call all methods need for importing data from Woo into Odoo, including import taxes, customers, products and orders.

[](https://www.notion.so/a96e0db1389e411fbf041b5c4ab6d42b#97318652f43f4935b8437f50ad5c43f7)

  *Picture 2. Woo Commerce Scheduling tab*

## Connect with Woo Commerce Shop

In the class explained above we use methods for creating and  testing connection with the Woo Shop.

In order to create connection  with any Woo Commerce Shop  and easily interact with the Woo Commerce REST API you need to install the `woocomerce` Python library. This is a Python wrapper for the Woo Commerce REST API.

**Installation**

    pip3 install woocommerce

Using the `woocommerce` library we are going to create `wcapi` object and use it in order to create connection with the shop.

The setup of the `wcapi` object is straightforward method shown in the code bellow. 
All we need to do is to provide the correct credentials to the API. 

    def create_woo_commerce_object(self):
            wcapi = API(
                url=self.check_woo_url(self.woo_host),
                consumer_key=self.woo_consumer_key,
                consumer_secret=self.woo_consumer_secret,
                wp_api="wp-json",
                version=self.woo_commerce_version if self.woo_commerce_version != '-1' else 'wc/v3')
            return wcapi

The API method has many options as input fields, only three of them are required. The required ones are :

`url`, `consumer_key` and `consumer_secret`. 
The full list of options for `woocommerce` API can be found [**here](https://pypi.org/project/WooCommerce/)** .

After the creation of the `wcapi`, we test the connection with the method `woo_test_connection`. This method basically checks if the connection is successful or not. The method is triggered by click on the button `Test Connection` shown in the *Picture 1.*
In case of successful connection a pop up is shown and in case of failure connection, an error is raised. 

# Import / Update  Taxes

Importing taxes from Woo Commerce into Odoo is process in two steps. The first one is importing taxes from Woo. 
After importing all the taxes the next step is to map them with the Odoo taxes that the customer wish to be used.

For importing taxes from Woo Commerce we are using the class `'woo.taxes'` . This is custom class created to store Woo taxes into Odoo database.  The following code is showing all fields needed in order to import taxes data. 

        woo_tax_id = fields.Integer(string='Woo Tax ID')
        country = fields.Char(string='Country code')
        state = fields.Char(string='State code')
        postcode = fields.Char(string='Postcode / ZIP ')
        city = fields.Char(string='City')
        rate = fields.Float(string='Rate % ')
        name = fields.Char(string='Tax name')
        channel_id = fields.Many2one('channel.pos.settings', string='Channel')
        tax_class = fields.Char(string='Class')

Woo taxes data can be imported by click on the button `Import taxes` in Taxes tab of the channel or automatically with the crone. The method for importing taxes is called `import_woo_taxes` and it is located in `channel.pos.settings` class. 

The pseudo code for this method is shown in *Picture3.*
First we create wcapi object and get all taxes with the `get`  call:

    wcapi.get('taxes').json()

Then we loop all the taxes and check if the tax exist. 
If exist then check if need to be updated, if yes - update tax, 
if no -  go in the next tax. If the tax does not exist then create it and store the tax data. 

After successful import of taxes the next step is to map the with Odoo taxes. For the mapping we use the custom class `'woo.taxes.map'`. This class contains only 3 fields.

 

        woo_tax = fields.Many2one('woo.taxes', required=True)
        odoo_tax = fields.Many2one('account.tax', string='Odoo mapped tax', required=True)
        woo_channel_id = fields.Many2one('channel.pos.settings', string='Channel Instance ID', readonly=True)

The fields are self explanatory. We have here one filed for the woo tax, another for the odoo tax and one for the channel id. 
The mapped taxes are showed in the `Taxes` tab of the Channel. 
You can see this view in *Picture 4.* 

# Import / Update  Customers

[](https://www.notion.so/a96e0db1389e411fbf041b5c4ab6d42b#16b39962a1e74e8d86a31ec280375f59)

Picture 3. Pseudo code for Importing taxes from Woo into Odoo

[](https://www.notion.so/a96e0db1389e411fbf041b5c4ab6d42b#f28649be1b644d3cbc7fdf341d3e2974)

Picture 4. Woo Commerce Taxes tab

Importing customers is a method used for import customers from Woo Commerce into Odoo. Similar as import taxes, this function can be called automatically or manual,  by clicking on `"Import customers"` button in the Customers tab of the Channel. All customer data will be imported including general information, billing and shipping info.

For this purpose we use the function `import_woo_customers` located in `channel.pos.settings` class.
*Picture5*  shows the pseudo code for importing customers.

Again with wcapi we get all customer data. 

    wcapi.get('customers').json()

We go through all customers. 
The same logic as importing taxes is used. 

1. First  check if the customer exist. 
2. If exist then check if the customer have been updated.
    1. If is updated, update customer data in Odoo. 
    2. If not updated go to the next customer. 
3. Else if the customer does not exist, create record in `res.partner` for the current customer. 

[](https://www.notion.so/a96e0db1389e411fbf041b5c4ab6d42b#ea7e7f3cb1764e308a5fd0b8c8cd37d7)

Picture 5. Pseudo code for Importing customers from Woo into Odoo

# Import /  Products

Import products also can be called both manual and automatically. Import products button can be found in the `Products` tab on the Channel. This function is used for importing sample products and products with variants from Woo Commerce into Odoo. While importing all product data is imported including name, description, prices, stock, images, attributes, variants etc.

Import products is done using `import_woo_products` methods. Same as the previous method for importing, this method is also located in the `channel.pos.settings`  class.
This method is for importing and updating product data and information. 

As we can see the pseudo code in `Picture6`, we are using similar logic as before.
We get product data with the following API call:

    wcapi.get('products').json()

After getting the products data in `json` format we process  it with the following steps: 

1. Check if master product exist
2. If master product exist
    1.  Check if woo clone exist
        1. If the clone exist check for update
        2.  If the product need to be updated then update                           product data
        3. If there is no need of update go to the next product
    2. If the clone does not exist - create clone record  in `product.template`
3. If master product does not exist - create master record  in `product.template`
    1. Create woo clone record in `product.template`

[](https://www.notion.so/a96e0db1389e411fbf041b5c4ab6d42b#dd1d483c9ba244f590dce3dbfe8226db)

Picture 6. Pseudo code for Importing products from Woo into Odoo

# Export Products

Export product is a method for exporting products from Odoo into Woo. Basically this function is inverse to the import function. Same as importing, while exporting all product data is exported from Odoo into Woo.  
Product export can be done in 2 ways:

- for single product
- for multiple products.

The same logic is used for both ways. The pseudo code is shown in *Picture7.* 
For exporting products is used the method `export_woo_products.` In addition are the steps for export products. 

1. Create dictionary for fill in with product data
2. Check for image medium - if exist add image data to the product dict
3. Check for additional product images - if exist some  add them to the product dict
4. Check for product variants - if variants exist then add them too in the product dict
5. Check if the product exist in Woo
    1. If exist update product data with the following API call:

        wcapi.post('products', product_data)

    2. If not exist - create the product into Woo Shop with the next API call : 

        wcapi.put('products/woo_id', product_data

[](https://www.notion.so/a96e0db1389e411fbf041b5c4ab6d42b#1e738236d3d64acaafb898c188d5cc42)

Picture 7. Pseudo code for Exporting products from Odoo into Woo Commerce

# Import / Update Orders

In the tab for `Orders`, there will be a list of all imported sale orders directly from the Woo Commerce Shop. 

Similarly to the rest of these tabs, these data entries will be added automatically with a periodic function, but there also will be a button `"Import Orders"` present, that will manually perform this action.

For performing this action `import_woo_orders` method is used.  And again this method is location in  `channel.pos.settings` class.
The logic of importing / updating orders is same as before. 

1. Check if the order exist. 
2. If exist then check if the order have been updated.
    1. If is updated, update order data in Odoo. 
    2. If not updated go to the next order. 
3. Else if the order does not exist, create record in `sale.order`  for the current order. 

The pseudo code for import orders is in *Picture8.*

[](https://www.notion.so/a96e0db1389e411fbf041b5c4ab6d42b#d8a3aef464744013b1ee0b4d4e11017c)

Picture 8. Pseudo code for Importing orders from Woo into Odoo

# Log Information

All Log  information is shown in the Scheduling tab on the Channel. Here we show all info from the methods execution.
The information table contains data as type of the log, message (description), date and time.