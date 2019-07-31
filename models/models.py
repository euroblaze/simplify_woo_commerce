# -*- coding: utf-8 -*-

from odoo import models, fields, api

#======================================================== PSEUDOCODE ======================================================================
#  WooCommerce Channel will inherit channel.pos.settings class and additionally in the following pseudocode will be added the fields required.
#  The chanel will contain 7 tabs:
#     - Api configuration to configure the Woo Commerce Shop
#     - Products - list/tree view with all products in Woo Commerce
#     - Customers - list/tree view with all customers in Woo Commerce
#     - Orders - list/tree view with all orders in Woo Commerce
#     - Taxes - table of mapped taxes
#     - Automation - shows fields for choosing frequency of importing and updating data
#     - Logs - shows all logs
#
# # 1. Connect WooCommerce Shop / Api Configuration
#     class WooCommerce()
#         inherit the channel.pos.settings class
#         #inherit the pos field and add selection with ID for wooCommerce
#         pos = pos.addSelection(['3', 'Woo Commerce'])
#         # add fields for the api configuration
#         woo_host = hostname (char)
#         woo_username = username (char)
#         woo_password = password (char)
#         woo_consumer_key = consumer_key (char)
#         woo_consumer_secret = consumer_secret (char)
#         create wcapi instance with the fields above.
#
#         #add fields for automation:
#           woo_last_update_product = date of the last product update
#           woo_last_update_oder = date of the last quotation/sale_order update
#           woo_last_update_customer = date of the last customer update
#           woo_last_update_tax = date of the last tax update

#
#
#         def test_woo_connection():
#             try:
#                 if wcapi is created
#                     check the connection
#                     log successful connection
#             except:
#                 raise Exception("Woo Commerce connection failed :( ")
#                 log failed connection
#                 return True
#
# # 2. Products import (WooCommerce -> Odoo)
#         def import_woo_products():
#             import_date_odoo = date of last import in odoo
#             woo_products = get woo_products where date_created > import_date_odoo
#             switch(woo_products){
#                 case object list:
#                     for product in woo_products:
#                      if does not exist master product in odoo
#                         create master_product
#                         if master_product is created:
#                             log successful creation of master_product in odoo
#                         else:
#                             log error while creating master product
#                     #when master product excist or is created now, next step is to create clone product for woo
#                     create clone_product (woo-> odoo)
#                     if clone_product is created:
#                         log successful creation
#                     else:
#                         log error while creation
#                     break
#                 case 0:
#                     log no creation
#                     break
#                 case false: #unsuccessful import from woo_commerce
#                     log error
#                     break
#             }
#                 return True
# # 3. Products update (WooCommerce -> Odoo)
#         def update_woo_products: #update only woo clones (with chanel-id for woo)
#             update_date_odoo = date of the last update in odoo (woo clones) products
#             woo_products = get products from woo where date_modified > update_date_odoo
#             switch (woo_products){
#                 case object list:
#                     for product in woo_products:
#                         update product in odoo
#                         if product is updated:
#                             log successful update
#                          else:
#                             log error while updating
#                     break
#                 case 0:
#                     log noupdate
#                     break
#                 case false:  #unsuccessful import from woo_commerce
#                     log error
#                     break
#             }
#           return True
#
# #4. Products export (Odoo -> WooCommerce. Export new products created or edited in Odoo to WooCommerce)
# # when some change is made to a product in odoo sync the change to the woo product
#         # 4.1 Export product in woo when a new product is created in odoo (overwrite create product function)
#             def create(self);
#                 res = call the super function for creating product
#                 check if the created product is woo clone produc
#                 if woo_clone_product:
#                     create new product in wooCommerce
#                     if new product is successfully created in wooCommerce:
#                         log successful creation of product in Odoo and Woo
#                     else :
#                         log error while
#                 return res
#
#         # 4.2 Export product in woo when a (clone)product is updated in odoo (overwrite edit/write product function)
#             def write(self):
#                 res = call the super function for edit product
#                 check if the edited product is woo clone product
#                 if woo_clone_product:
#                     update product in odoo:
#                     if product is updated:
#                         log successful update
#                     else:
#                         log error while updating product
#                 return res
# # 5. Update deleted products
#     #5.1 Odoo -> Woo Commerce
#     #Overwrite delete/unlink function
#     def unlink(self):
#         res  = call super function for deleting update_odoo_product
#         check if channel_id is woo_commerce:
#             get woo_id from the product to be deleted
#             delete product with woo_id in woo_commerce_products
#             if product is successfully deleted:
#                 log product successfully deleted
#             else :
#                 log delete failed
#
#     #5.2 Woo Commerce -> Odoo
#     def update_deleted_products_from_woo():
#         woo_product_ids = get all ids from the products in woo
#         odoo_product_ids = get all ids from the clone products for woo in product.template
#         #compare this two lists with ids
#         for woo_id in woo_product_ids:
#             if woo_id not in odoo_product_ids:
#                 delete product from odoo
#                 if delete product is successful:
#                     log product deleted
#                 else:
#                     log error while deleting product
# # 6. Customers import (Woo -> Odoo)
#     def import_woo_customers():
#         import_date = date of the last import in odoo
#         woo_customers = get all customers from wooCommerce where date_created > import_date
#         switch(woo_customers){
#             case object list:
#                 for customer in woo_customers:
#                     create customer in odoo
#                     if the customer is created:
#                         log successful creation of customer in odoo
#                     else:
#                         log error while creating customer
#             case 0:
#                 log nocreation
#                 break
#             case false: #unsuccessful import from woo_commerce
#                 log error
#                 break
#         }
# # 7. Customers update (Woo -> Odoo)
#     def update_woo_customers():
#         update_date = date of the last update in odoo customers
#         woo_customers = get all customers from wooCommerce where date_modified > update_date
#         switch (woo_customers){
#             case object list:
#                 for customer in woo_customers:
#                     update customer in odoo
#                     if customer is updated:
#                         log successful update of customer
#                     else:
#                         log error while updating customer
#                 break
#             case 0:
#                 log noupdate
#                 break
#             case false:
#                 log error
#                 break
#         }
# # 8. Update deleted customers (Woo -> Odoo)
#     def update_deleted_woo_customers():
#         woo_customer_ids = get all ids from the customers in woo
#         odoo_customer_ids = get all ids from customers for woo in res_partner
#         #compare this two lists with ids
#         for woo_id in woo_customer_ids:
#             if woo_id not in odoo_customer_ids:
#                 delete customer from odoo
#                 if delete customer is successful:
#                     log customer deleted
#                 else:
#                     log error while deleting customer
#
# 9. Quotations import
#       def import_woo_qoutation():
#         import_date = date of the last import in odoo sale_order
#         woo_quotations = get all quotations from wooCommerce where create_date > update_date
#         switch (woo_quotaions){
#             case object list:
#                 for quotation in woo_quotation:
#                     update quotation in odoo
#                      set state to confirmed
#                     if quotation is updated:
#                         log successful update of quotation
#                     else:
#                         log error while updating quotation
#                 break
#             case 0:
#                 log noupdate
#                 break
#             case false:
#                 log error
#                 break
#         }

# 10. Taxes import
#     def import_woo_taxes():
#         import_date = date of the last import in odoo
#         woo_taxes = get all Taxes from wooCommerce where date_created > import_date
#         switch(woo_Taxes){
#             case object list:
#                 for tax in woo_taxes:
#                     create tax in odoo
#                     if the tax is created:
#                         log successful creation of tax in odoo
#                     else:
#                         log error while creating taxes
#             case 0:
#                 log nocreation
#                 break
#             case false: #unsuccessful import from woo_commerce
#                 log error
#                 break
#         }
# 12. Taxes update
#     def update_woo_taxes():
#         update_date = date of the last update in odoo taxes (account.tax)
#         woo_taxes = get all taxes from wooCommerce where date_modified > update_date
#         switch (woo_taxes){
#             case object list:
#                 for tax in woo_taxes:
#                     update tax in odoo
#                     if tax is updated:
#                         log successful update of tax
#                     else:
#                         log error while updating taxes
#                 break
#             case 0:
#                 log noupdate
#                 break
#             case false:
#                 log error
#                 break
#         }
# #10. Set Automation settings (Woo->Odoo)
#     #Create cron for periodical  synchronization depending on the timestamps chosen in the Automation tab on the channel
#      def auto_update_woo():
#             update products
#             update customers
#             update quotations
#             update taxes

# #Create new class to inherit product.template
#     class WooProductTemplate():
#         _inherit = 'product.template'
# #add additional fields for wooCommerce
#     woo_id = id of the product in wooCommerce (Integer/Char)
#     woo_categories = many2many to the product_categories
#     woo_variants = product woo_variants
#     # if necessary later will add more fields here
#
#     #4.1 and 4.2 (create and write product) will be overwritten here
#         # 4.1 Export product in woo when a new product is created in odoo (overwrite create product function)
#             def create(self);
#                 res = call the super function for creating product
#                 check if the created product is woo clone product
#                 if woo_clone_product:
#                     create new product in wooCommerce
#                     if new product is successfully created in wooCommerce:
#                         log successful creation of product in Odoo and Woo
#                     else :
#                         log error while
#                 return res
#
#         # 4.2 Export product in woo when a (clone)product is updated in odoo (overwrite edit/write product function)
#             def write(self):
#                 res = call the super function for edit product
#                 check if the edited product is woo clone product
#                 if woo_clone_product:
#                     update product in odoo:
#                     if product is updated:
#                         log successful update
#                     else:
#                         log error while updating product
#                 return res
#         Unlink deleted products will be also overwritten in product_template
#         # 5. Update deleted products
#             #5.1 Odoo -> Woo Commerce
#             #Overwrite delete/unlink function
#             def unlink(self):
#                 res  = call super function for deleting update_odoo_product
#                 check if channel_id is woo_commerce:
#                     get woo_id from the product to be deleted
#                     delete product with woo_id in woo_commerce_products
#                     if product is successfully deleted:
#                         log product successfully deleted
#                     else :
#                         log delete failed
# #Create new class to inherit res.partner
#     class WooCustomers():
#         _inherit = 'res.partner'
#         woo_customer_id = id of customer in WooCommerce (Integer/String)
#         #later will add more fields if necessary
#
# #Create new class for woo taxes
#     class ChannelWooTaxes():
#         #add fields in the class/ if needed later will add more fields
#         woo_tax_id = fields.Char('Woo Commerce ID', default='3')
#         name = tax name (char)
#         amount = tax amount (float)
#         woo_chanel_id = Channel( Many2one with channel.pos.settings)
#         account_tax =Mapped tax with odoo (many2one with account tax)
#
#         #add function for mapping taxes (Woo->Odoo)
#             #first check if you can take the taxes from woo with api call, if not create them
#           def map_woo_taxes():
#               map every woo_tax with odoo_tax
#
# Create new class to inherit sale order
#     class WooQuotatins():
#         _inherit = 'sale.order'
#         woo_quotation_id = id of qoutaion in WooCommerce (Integer/String)


















