# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError, RedirectWarning, UserError
from .. python_magic_0_4_11 import magic
from .. wordpress_xmlrpc import base
from .. wordpress_xmlrpc import compat
from .. wordpress_xmlrpc import media
import base64
import tempfile

class SpecialTransport(compat.xmlrpc_client.Transport):
    user_agent = 'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.43 Safari/537.31'


def upload_image(image_data, image_name, host, username, password):
    if not image_data or not image_name:
        return {}
    client = base.Client('%s/xmlrpc.php' % (host), username,
                         password, transport=SpecialTransport())
    data = base64.decodestring(image_data)
    # create a temporary file, and save the image
    fobj = tempfile.NamedTemporaryFile(delete=False)
    filename = fobj.name
    fobj.write(data)
    fobj.close()
    mimetype = magic.from_file(filename, mime=True)
    # prepare metadata
    data = {
        'name': '%s_%s.%s' % ("image", image_name, mimetype.split(b"/")[1].decode('utf-8')),
        'type': mimetype,  # mimetype
    }

    # read the binary file and let the XMLRPC library encode it into base64
    with open(filename, 'rb') as img:
        data['bits'] = compat.xmlrpc_client.Binary(img.read())

    res = client.call(media.UploadFile(data))
    return res


#INHERT PRODUCT_TEMPLATE AND ADD NEW FIELDS FOR WOO_CHANNEL INSTANCE ID
class InhertProductTemplate(models.Model):
    _inherit = 'product.template'

    woo_product_id = fields.Integer(string='Woo Product ID')
    woo_sale_price = fields.Float(string='Woo Sale price', description="Price when the product is on sale")
    woo_regular_price = fields.Float(string='Woo Regular price', description="Regular price of the product")
    woo_sku = fields.Char("Woo SKU")

    def _compute_pos(self):
        if self.channel_id:
            self.pos = self.channel_id.pos
            print("POS", self.pos)

    pos = fields.Integer(string='Channel pos', compute=_compute_pos)


    @api.depends('product_variant_ids', 'product_variant_ids.default_code')
    def _compute_default_code(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)

        if self.woo_sku is not None:
            self.default_code = self.woo_sku
        else:
            for template in unique_variants:
                template.default_code = template.product_variant_ids.default_code
            for template in (self - unique_variants):
                template.default_code = ''


    def toggle_active(self):
        super(InhertProductTemplate, self).toggle_active()
        for record in self:
            if not record.active and (int(record.channel_id.pos) == 3):
                woo_id = record.woo_product_id
                data = {
                    'catalog_visibility': 'hidden',
                    'status': 'draft'
                }
                wcapi = record.channel_id.create_woo_commerce_object()
                wcapi.put("products/%s"%(woo_id), data)

            elif record.active and (int(record.channel_id.pos) == 3):
                woo_id = record.woo_product_id
                data = {
                    'catalog_visibility': 'visible',
                    'status': 'publish'
                }
                wcapi = record.channel_id.create_woo_commerce_object()
                wcapi.put("products/%s" % (woo_id), data)

    # def export_woo_products(self, records):
    #     for product in records:
    #         print(int(product.channel_id.pos) == 3)
    #         if int(product.channel_id.pos) == 3:
    #
    #
    #             woo_id = product.woo_product_id
    #             data ={}
    #             wcapi = product.channel_id.create_woo_commerce_object()
    #             print("API", wcapi.__dict__)
    #
    #             taxes = self.env['woo.taxes.map'].search([('woo_channel_id', '=', product.channel_id.id)])
    #             taxes_class = []
    #             if len(product.taxes_id) > 0:
    #                 for tax in taxes:
    #                     if tax.odoo_tax in product.taxes_id:
    #                         taxes_class.append(tax.woo_tax.tax_class)
    #
    #
    #
    #
    #
    #             categories = []
    #             print("Product category", product.categ_id)
    #             categ_id = product.categ_id
    #             parent_path = categ_id.parent_path.split("/")
    #
    #             for category in parent_path:
    #
    #                 if category != '':
    #                     print("************ category *************", category)
    #                     categ_id = self.env['product.category'].search([('id', '=', category)])
    #                     print("************ odo category **********", categ_id)
    #                     categ_data = {
    #                         'name': categ_id.name,
    #                     }
    #                     if categ_id.woo_channel_id: # this category exist in Woo -> update the category
    #                         print("Category exist in Woo")
    #                         woo_categ = wcapi.put("products/categories/%s" %(categ_id.woo_category_id), categ_data)
    #                         categ_data['id'] = categ_id.woo_category_id
    #
    #
    #                     else: # the category does not exist in Woo -> create the category in Woo
    #                         if categ_id.parent_id == None:
    #                             print('Category does not exist in Woo')
    #                             categ_id.write({'woo_channel_id': product.channel_id.id})
    #                             print("CATEG ID", categ_id.woo_channel_id)
    #                             category = wcapi.post("products/categories", categ_data).json()
    #                             print("CATEGORY", category)
    #                             categ_id.woo_category_id = category['id']
    #                             categ_data['id'] = category['id']
    #                             print("CATEGORY",  categ_data['id'])
    #                         else:
    #                             print('Category does not exist in Woo')
    #                             categ_data['parent'] = categ_id.parent_id.woo_category_id
    #                             categ_id.write({'woo_channel_id': product.channel_id.id})
    #                             print("CATEG ID", categ_id.woo_channel_id)
    #                             category = wcapi.post("products/categories", categ_data).json()
    #                             print("CATEGORY", category)
    #                             categ_id.woo_category_id = category['id']
    #                             categ_data['id'] = category['id']
    #                             print("CATEGORY", categ_data['id'])
    #
    #
    #
    #                     categories.append(categ_data)
    #
    #             print("CATEGORIES ********************", categories[-1])
    #
    #
    #
    #             # get product images
    #             images = []
    #             image_medium = product.image_medium  # binary data of product image medium
    #             print('Image MEDIUM', image_medium)
    #             if image_medium:
    #                 res = upload_image(image_medium, product.name, product.channel_id.woo_host,
    #                                    product.channel_id.woo_username, product.channel_id.woo_password)
    #                 image = {
    #                     'id': res['attachment_id'],
    #                     'src': res['link'],
    #                     'name': res['title']
    #                 }
    #                 images.append(image)
    #             print("PRODUCT IMAGES", len(product.product_image_ids)>0 )
    #             if len(product.product_image_ids) > 0:
    #                 for image in product.product_image_ids:
    #                     print("IMAGE", image.image)
    #                     res = upload_image(image.image, image.name, product.channel_id.woo_host, product.channel_id.woo_username, product.channel_id.woo_password)
    #                     image = {
    #                         'id': res['attachment_id'],
    #                         'src': res['link'],
    #                         'name': res['title']
    #                     }
    #                     images.append(image)
    #                 data['images'] = images
    #                 print("IMAGES", images)
    #             print(product.default_code)
    #             print("EXPORT PRODUCT STOCK ", product.qty_available)
    #
    #             data.update({
    #                 'name': product.name,
    #                 'description': product.description if product.description else ' ',
    #                 'sku':product.default_code if product.default_code else ' ',
    #                 'price': str(product.lst_price),
    #                 'regular_price': str(product.woo_regular_price),
    #                 'sale_price': str(product.woo_sale_price) if product.woo_sale_price != 0 else ' ',
    #                 'tax_class': taxes_class[0] if len(taxes_class) > 0 else " ",
    #                 'stock_quantity': product.qty_available,
    #                 'weight': str(product.weight),
    #                 'categories': [categories[-1]],
    #
    #             })
    #             print("DATA", data)
    #
    #
    #             # If the product exist in Odoo but not in Woo, create the product in Woo
    #             print("WOO ID ", woo_id)
    #             if woo_id == 0:
    #                 woo_product = wcapi.post("products", data).json()
    #                 print("create product ", woo_product)
    #                 print("WOO PRODUCT", woo_product)
    #                 woo_id = woo_product['id']
    #                 product.write({'woo_product_id': woo_id})
    #
    #             #If woo id exist update the product in Woo
    #             # if the product has variant update/create the variants too
    #             attributes = product.attribute_line_ids
    #             print('Attributes', attributes)
    #             if len(attributes) > 0:
    #                 variants = self.env['product.product'].search([('product_tmpl_id', '=', product.id)])
    #                 variations = []
    #                 variant_data = {}
    #                 data['type'] = 'variable'
    #                 for variant in variants:
    #                     print("VARIANT WOO ID", variant.woo_variant_id )
    #                     print("variant weight", str(variant.weight))
    #
    #
    #                     variant_data = {
    #                             'description': variant.description,
    #                             'price': str(variant.lst_price),
    #                             'regular_price': str(variant.lst_price),
    #                             'tax_class': taxes_class[0] if len(taxes_class) > 0 else None,
    #                             'stock_quantity': variant.qty_available,
    #                             'weight': str(variant.weight),
    #                         }
    #                     image = {}
    #                     image_medium = variant.image_medium  # binary data of product image medium
    #                     if image_medium is not None:
    #                         res = upload_image(image_medium, str(product.name)+str(variant.id), product.channel_id.woo_host,
    #                                            product.channel_id.woo_username, product.channel_id.woo_password)
    #                         image = {
    #                             'id': res['attachment_id'],
    #                             'src': res['link'],
    #                             'name': res['title']
    #                         }
    #
    #                         variant_data['image'] = image
    #                      # Add attributes
    #                     attributes = []
    #                     variant_attributes = variant.attribute_value_ids
    #                     for attribute in variant_attributes:
    #                         attribute_data = {}
    #                         attribute_data['name'] = attribute.attribute_id.name
    #                         attribute_data['option'] = attribute.name
    #                         attributes.append(attribute_data)
    #                     variant_data['attributes'] = attributes
    #
    #                     # Add woo ID if exist -> update variant
    #                     if variant.woo_variant_id:
    #                         variant_data['id'] = variant.woo_variant_id
    #                         print("Update variant", wcapi.put("products/%s/variations/%s" % (woo_id, variant.woo_variant_id), variant_data).json())
    #
    #                     else: # -> create variant
    #                         print("Woo ID", woo_id)
    #                         print("Variant Data", variant_data)
    #                         var = wcapi.post("products/%s/variations" % (woo_id), variant_data).json()
    #                         print("Create variant", var)
    #                         variant_data['id'] = var['id']
    #
    #                     variations.append(variant_data['id'])
    #                     # create/update variant and then get the variant id
    #                 data['variations'] = variations
    #             print("Update product", wcapi.put('products/%s'% (woo_id), data).json())
    
    def export_woo_product(self):
        product = self
        if int(product.channel_id.pos) == 3:


            woo_id = product.woo_product_id
            # data = {'manage_stock': 'true'}
            data = {}
            wcapi = product.channel_id.create_woo_commerce_object()
            print("API", wcapi.__dict__)

            taxes = self.env['woo.taxes.map'].search([('woo_channel_id', '=', product.channel_id.id)])
            taxes_class = []
            if len(product.taxes_id) > 0:
                for tax in taxes:
                    if tax.odoo_tax in product.taxes_id:
                        taxes_class.append(tax.woo_tax.tax_class)

            categories = []
            print("Product category", product.categ_id)
            categ_id = product.categ_id
            parent_path = categ_id.parent_path.split("/")

            for category in parent_path:

                if category != '':
                    print("************ category *************", category)
                    categ_id = self.env['product.category'].search([('id', '=', category)])
                    print("************ odoo category **********", categ_id)
                    categ_data = {
                        'name': categ_id.name,
                    }
                    if categ_id.woo_category_id:  # this category exist in Woo -> update the category
                        print("Category exist in Woo")
                        woo_categ = wcapi.put("products/categories/%s" % (categ_id.woo_category_id), categ_data)
                        categ_data['id'] = categ_id.woo_category_id


                    else:  # the category does not exist in Woo -> create the category in Woo
                        if categ_id.parent_id == None:
                            print('Category does not exist in woo and does not have parent')
                            categ_id.write({'channel_id': product.channel_id.id})
                            print("CATEG ID", categ_id.woo_channel_id)
                            category = wcapi.post("products/categories", categ_data).json()
                            print("CATEGORY", category)
                            categ_id.woo_category_id = category['id']
                            categ_data['id'] = category['id']
                            print("CATEGORY", categ_data['id'])
                        else:
                            print('Category does not exist in Woo')
                            categ_data['parent'] = categ_id.parent_id.woo_category_id
                            print("CATEG DATA", categ_data)
                            categ_id.write({'channel_id': product.channel_id.id})
                            print("CATEG ID", categ_id.channel_id)
                            category = wcapi.post("products/categories", categ_data).json()
                            print("CATEGORY", category)
                            categ_id.woo_category_id = category['id']
                            categ_data['id'] = category['id']
                            print("CATEGORY", categ_data['id'])

                    categories.append(categ_data)

            print("CATEGORIES ********************", categories[-1])

            # get product images
            images = []
            image_medium = product.image_medium  # binary data of product image medium
            print('Image MEDIUM', image_medium)
            if image_medium:
                res = upload_image(image_medium, product.name, product.channel_id.woo_host,
                                   product.channel_id.woo_username, product.channel_id.woo_password)
                image = {
                    'id': res['attachment_id'],
                    'src': res['link'],
                    'name': res['title']
                }
                images.append(image)
            print("PRODUCT IMAGES", len(product.product_image_ids) > 0)
            if len(product.product_image_ids) > 0:
                for image in product.product_image_ids:
                    print("IMAGE", image.image)
                    res = upload_image(image.image, image.name, product.channel_id.woo_host,
                                       product.channel_id.woo_username, product.channel_id.woo_password)
                    image = {
                        'id': res['attachment_id'],
                        'src': res['link'],
                        'name': res['title']
                    }
                    images.append(image)
            data['images'] = images
            print("IMAGES", images)
            print(product.default_code)
            print("EXPORT PRODUCT STOCK ", product.qty_available)

            data.update({
                'name': product.name,
                'description': product.description if product.description else ' ',
                'sku': product.default_code if product.default_code else ' ',
                'price': str(product.list_price),
                'regular_price': str(product.woo_regular_price) if product.woo_regular_price != 0.0 else str(product.list_price),
                'sale_price': str(product.woo_sale_price) if product.woo_sale_price != 0 else ' ',
                'tax_class': taxes_class[0] if len(taxes_class) > 0 else " ",
                'manage_stock': 'true',
                'stock_quantity': product.qty_available,
                'weight': str(product.weight),
                'categories': [categories[-1]],
                'status': 'publish'

            })
            print("DATA", data)

            # If the product exist in Odoo but not in Woo, create the product in Woo
            print("WOO ID ", woo_id)
            if woo_id == 0:
                woo_product = wcapi.post("products", data).json()
                print("create product ", woo_product)
                print("WOO PRODUCT", woo_product)
                woo_id = woo_product['id']
                product.write({'woo_product_id': woo_id})

            # If woo id exist update the product in Woo
            # if the product has variant update/create the variants too
            attributes = product.attribute_line_ids
            print('Attributes', attributes)
            if len(attributes) > 0:
                for attribute in attributes:
                    values = attribute.value_ids
                    for value in values:
                        attribute_data = {
                            "name": value.name,
                            "type": "select",
                        }
                        # print(wcapi.post("products/attributes", attribute_data).json())
                        print("Value name", value.name)
                variants = self.env['product.product'].search([('product_tmpl_id', '=', product.id)])
                variations = []
                variant_data = {}
                data['type'] = 'variable'
                wcapi.put('products/%s' % (woo_id), data).json()
                for variant in variants:
                    print("VARIANT WOO ID", variant.woo_variant_id)
                    print("variant weight", str(variant.weight))

                    variant_data = {
                        'description': variant.description,
                        'price': str(variant.lst_price),
                        'regular_price': str(variant.lst_price),
                        'tax_class': taxes_class[0] if len(taxes_class) > 0 else None,
                        'stock_quantity': variant.qty_available,
                        'weight': str(variant.weight),
                    }
                    image = {}
                    image_medium = variant.image_medium  # binary data of product image medium
                    if image_medium is not None:
                        res = upload_image(image_medium, str(product.name) + str(variant.id),
                                           product.channel_id.woo_host,
                                           product.channel_id.woo_username, product.channel_id.woo_password)
                        image = {
                            'id': res['attachment_id'],
                            'src': res['link'],
                            'name': res['title']
                        }

                        variant_data['image'] = image
                    # Add attributes
                    attributes = []
                    variant_attributes = variant.attribute_value_ids
                    for attribute in variant_attributes:
                        attribute_data = {}
                        attribute_data['name'] = attribute.attribute_id.name
                        attribute_data['option'] = attribute.name
                        attributes.append(attribute_data)
                        print("CREATE ATTRIBUTE", wcapi.post("products/attributes", {"name": attribute.attribute_id.name}).json())
                    # variant_data['attributes'] = attributes

                    # Add woo ID if exist -> update variant
                    if variant.woo_variant_id:
                        variant_data['id'] = variant.woo_variant_id
                        print("Update variant",
                              wcapi.put("products/%s/variations/%s" % (woo_id, variant.woo_variant_id),
                                        variant_data).json())

                    else:  # -> create variant
                        print("Woo ID", woo_id)
                        print("Variant Data", variant_data)
                        var = wcapi.post("products/%s/variations" % (woo_id), variant_data).json()
                        print("Create variant", var)
                        variant_data['id'] = var['id']

                    variations.append(variant_data['id'])
                    # create/update variant and then get the variant id
                data['variations'] = variations
            print("Update product", wcapi.put('products/%s' % (woo_id), data).json())
            view_id = self.env.ref('simplify_woo_commerce.woo_alert_window').id
            message = 'Product successfully exported to Woo Commerce!'
            return {
                'name': 'Information',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(view_id, 'form')],
                'res_model': 'custom.pop.up.message',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {'default_message': message},
            }











