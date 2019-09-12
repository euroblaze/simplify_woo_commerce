# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError, RedirectWarning, UserError
from odoo.addons import decimal_precision as dp

#INHERT PRODUCT_TEMPLATE AND ADD NEW FIELDS FOR WOO_CHANNEL INSTANCE ID
class InhertProductTemplate(models.Model):
    _inherit = 'product.template'

    # woo_channel_id = fields.Many2one('channel.pos.settings', string='Channel Instance ID', description="Woo Channel instance ID")
    woo_product_id = fields.Integer(string='Woo Product ID')
    woo_sale_price = fields.Float(string='Sale price', description="Price when the product is on sale")
    woo_regular_price = fields.Float(string='Regular price', description="Regular price of the product")
    woo_sku = fields.Char("Woo SKU")


    @api.depends('product_variant_ids', 'product_variant_ids.default_code')
    def _compute_default_code(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        # print("Unique variants", unique_variants)
        # print("Self in compute DEAFULT CODE ",  self)
        if self.woo_sku is not None:
            # print("WOO_SKU", self.woo_sku)
            # print("DEFAULT_CODE IN COMPUTE before", self.default_code)
            self.default_code = self.woo_sku
            # print("DEFAULT_CODE IN COMPUTE after", self.default_code)
        # for product in self:
        #     print("Product in COMPUTE", product)
        #     print("WOO_SKU", product.woo_sku)
        #     if product.woo_sku is not None:
        #         product.default_code = product.woo_sku
        #         print("DEFAULT_CODE IN COMPUTE", product.default_code)
        #         break
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

    def export_woo_products(self, records):
        for product in records:
            print(int(product.channel_id.pos) == 3)
            if int(product.channel_id.pos) == 3:
                woo_id = product.woo_product_id


                wcapi = product.channel_id.create_woo_commerce_object()

                print('product taxes', product.taxes_id)
                data = {
                    'name': product.name,
                    'description': product.description,
                    'sku': product.default_code,
                    'price': product.lst_price,
                    'regular_price': product.woo_regular_price if product.woo_regular_price else None,
                    'sale_price': product.woo_sale_price if product.woo_sale_price else None,
                }
                print(product)
                print(woo_id)
                print(wcapi.get("products/%s" % (woo_id)).json())

                if woo_id: #If woo id exist update the product in Woo
                    print()
                else: #If the product exist in Odoo but not in Woo, create the product in Woo
                    print()






