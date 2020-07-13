

# -*- coding: utf-8 -*-

from odoo import models, api

help_html = {
    'help_woo_conf': """
    <h2>Connect Woocommerce</h2>
                <div class="row">
                    <div class="col-lg-4">
                        <br>
                        <br>
                        <h3>Step 1: Login to Woocommerce Admin Panel</h3>
                        <br>
                        <br>
                        <p style="font-size: 15px; text-align: justify;">
                            The first thing you should do is to login to your shop so you 
                            can extract the data that is needed in order to make the connection to your Woo shop possible. 
                            <br><br>
                            To do this, in case you are not familiar with the Wordpress adminstration panel is to go to for example: your_shop_url.com/wp-admin
                            <br>
                            Once there, enter your credentials to login to your shop admin panel.
                        </p>
                    </div>
                    <div class="col-lg-8">
                        <img style="width: 100%" src="simplify_woo_commerce/static/help_html/images/login.png">         
                    </div> 
                </div>
                <div class="row" style="margin-top:10px">
                    <div class="col-lg-4">
                        <br>
                        <br>
                        <h3>Step 2: Find Woo Shop Version</h3>
                        <br>
                        <br>
                        <p style="font-size: 15px; text-align: justify;">
                            Once you're logged in the shop, you'll need find your woo shop version to fill in the Odoo configuration console.<br><br>
                            Go to: <br>
                            <b>WooCommerce/Status/System status</b><br>
                            Under WooCommerce version on the right side is your current version of your shop. Use this to select the appropriate version in the Odoo console.
                        </p>
                    </div>
                    <div class="col-lg-8">
                        <img style="width: 100%" src="simplify_woo_commerce/static/help_html/images/version.png">         
                    </div> 
                </div>
                <div class="row" style="margin-top:10px">
                    <div class="col-lg-4">
                        <br>
                        <br>
                        <h3>Step 3: Go to Your API section</h3>
                        <br>
                        <br>
                        <p style="font-size: 15px; text-align: justify;">
                            Next, you'll need to navigate to your API configuraiton tab.<br><br>
                            Navigate to: <br>
                            <b>WooCommerce/Advanced/REST API</b><br>
                            Once here you'll need to add a new key, that is, if you
                            don't already keep the consumer and consumer secret keys somewhere else.
                        </p>
                    </div>
                    <div class="col-lg-8">
                        <img style="width: 100%" src="simplify_woo_commerce/static/help_html/images/apitab.png">         
                    </div> 
                </div>
                <div class="row" style="margin-top:10px">
                    <div class="col-lg-4">
                        <br>
                        <br>
                        <h3>Step 4: Add new API key</h3>
                        <br>
                        <br>
                        <p style="font-size: 15px; text-align: justify;">
                            Click on the button <b>Add key</b> to open a form for creating a new
                            api key.<br>
                            <b>Description</b>: This is a free to describe text field. It can be used to describe the pourpose or usage of the key.<br>
                            <b>User</b>: Choose an appropriate user and take note of it's credentials so you will provide them in the odoo form.<br>
                            <b>Permissions</b>: Here you'll have to set Read/Write permissions.            
                        </p>
                    </div>
                    <div class="col-lg-8">
                        <img style="width: 100%" src="simplify_woo_commerce/static/help_html/images/new key form.png">  
                    </div> 
                </div>
                <div class="row" style="margin-top:10px">
                    <div class="col-lg-4">
                        <br>
                        <br>
                        <h3>Step 5: Generate the key, extract data</h3>
                        <br>
                        <br>
                        <p style="font-size: 15px; text-align: justify;">
                            Complete the shop process by generating a key. Click on the button Generate Api key.<br><br>
                            When the process is complete, don't navigate away but take note of the Consumer key and Consumer secret first, for you can only access them once per key, at this exact moment when this process is complete.<br>
                            <br>
                            With this complete, you will have all information to complete the connection to Odoo: Host(link to the shop), Username and Password(step 3), Consumer key and secret(Step 4)
                        </p>
                    </div>
                    <div class="col-lg-8">
                        <img style="width: 100%" src="simplify_woo_commerce/static/help_html/images/done key.png">  
                    </div> 
                </div>
    """,

}

class WooHelper(models.TransientModel):
    _name = 'woo.helper'

    @api.model
    def init_data(self):
        helpers = self.env['support_helper']
        for module in help_html.keys():
            res = helpers.search([('helper_name', '=', module)])
            if not res:
                helpers.create({'helper_name': module, 'html_body': help_html[module]})
