# -*- coding: utf-8 -*-

from odoo import models, fields, api

#======================================================== PSEUDOCODE ======================================================================
# 1. Connect WooCommerce Shop / Api Configuration
    class WooCommerce()
        inherit the channel.pos.settings class
        #inherit the pos field and add selection with ID for wooCommerce
        pos = pos.addSelection(['3', 'Woo Commerce'])
        # add fields for the api configuration
        woo_host = hostname (char)
        woo_username = username (char)
        woo_password = password (char)
        woo_comsumer_key = consumer_key (char)
        woo_consumer_secret = consumer_secret (char)
        create wcapi instace with the fields above.

        def test_woo_connection():
            try:
                if wcapi is created
                    check the connection
                    log successful connection
            except:
                raise Exception("Woo Commerce connection failed :( ")
                log failed connection

# 2. Products import (WooCommerce -> Odoo)
        def import_woo_products():
            import_date_odoo = date of last import in odoo
            woo_products = get woo_products where date_created > import_date_odoo
            switch(woo_products){
                case object list:
                    for product in woo_products:
                     if does not exict master product in odoo
                        create master_product
                        if master_product is created:
                            log succesfull creation of master_product in odoo
                        else:
                            log error while creating master product
                    #when master product excist or is created now, next step is to create clone product for woo
                    create clone_product (woo-> odoo)
                    if clone_product is created:
                        log succesfull creation
                    else:
                        log error while creation
                    break
                case 0:
                    log nocreation
                    break
                case false: #unsuccessful import from woo_commerce
                    log error
                    break
            }
# 3. Products update (WooCommerce -> Odoo)
        def update_odoo_products: #update only woo clones (with chanel-id for woo)
            update_date_odoo = date of the last update in odoo (woo clones) products
            woo_products = get products from woo where date_modified > update_date_odoo
            switch (woo_products){
                case object list:
                    for product in woo_products:
                        update product in odoo
                        if product is updated:
                            log successful update
                         else:
                            log error while updating
                    break
                case 0:
                    log noupdate
                    break
                case false:  #unsuccessful import from woo_commerce
                    log error
                    break
            }

#4. Products export (Odoo -> WooCommerce. Export new products created or edited in Odoo to WooCommerce)
# when some change is made to a product in odoo sync the change to the woo product
        # 4.1 Export product in woo when a new product is created in odoo (overwrite create product function)
            def create(self);
                res = call the super function for creating product
                check if the created product is woo clone produc
                if woo_clone_product:
                    create new product in wooCommerce
                    if new product is successfully created in wooCommerce:
                        log successful creation of product in Odoo and Woo
                    else :
                        log error while
                return res

        # 4.2 Export product in woo when a (clone)product is updated in odoo (overwrite edit/write product function)
            def write(self):
                res = call the super function for edit product
                check if the edited product is woo clone product
                if woo_clone_product:
                    update product in odoo:
                    if product is updated:
                        log successful update
                    else:
                        log error while updating product
                return res
# 5. Update deleted products
    #5.1 Odoo -> Woo Commerce
    #Overwrite delete/unlink function
    def unlink(self):
        res  = call super function for deleting update_odoo_product
        check if channel_id is woo_commerce:
            get woo_id from the product to be deleted
            delete product with woo_id in woo_commerce_products
            if product is successfuly deleted:
                log product successfuly deleted
            else :
                log delete failed
        return res
    #5.2 Woo Commerce -> Odoo
    def update_deleted_products_from_woo():
        woo_product_ids = get all ids from the products in woo
        odoo_product_ids = get all ids from the clone products for woo in product.template
        #compare this two lists with ids
        for woo_id in woo_product_ids:
            if woo_id not in odoo_product_ids:
                delete product from odoo
                if delete product is successful:
                    log product deleted
                else:
                    log error while deleting product
# 6. Customers import (Woo -> Odoo)
    def import_woo_customers():
        import_date = date of the last import in odoo
        woo_customers = get all customers from wooCommerce where date_created > import_date
        switch(woo_customers){
            case object list:
                for customer in woo_customers:
                    create customer in odoo
                    if the customer is created:
                        log succesfull creation of customer in odoo
                    else:
                        log error while creating customer
            case 0:
                log nocreation
                break
            case false: #unsuccessful import from woo_commerce
                log error
                break
        }
# 7. Customers update (Woo -> Odoo)
    def update_woo_customers():
        update_date = dete of the last update in odoo customers
        woo_customers = get all customers from wooCommerce where date_modified > update_date
        switch (woo_customers){
            case object list:
                for cutomer in woo_customers:
                    update customer in odoo
                    if customer is updated:
                        log successful update of customer
                    else:
                        log error while updating customer
                break
            case 0:
                log noupdate
                break
            case false:
                log error
                break
        }
# 8. Update deleted customers (Woo -> Odoo)
    def update_deleted_woo_customers():
        woo_customer_ids = get all ids from the custmers in woo
        odoo_customer_ids = get all ids from customers for woo in res_partner
        #compare this two lists with ids
        for woo_id in woo_customer_ids:
            if woo_id not in odoo_customer_ids:
                delete customer from odoo
                if delete customer is successful:
                    log customer deleted
                else:
                    log error while deleting customer


















