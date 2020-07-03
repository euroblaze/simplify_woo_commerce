# -*- coding: utf-8 -*-
from odoo import models, fields, api


def intersection(lst1, lst2):
    return [item for item in lst1 if item in lst2]

class ProductAttributeReMap(models.Model):
    _name = 'product.attribute.remap'

    def _compute_product(self):
        return self._context.get("product_id")

    @api.onchange('product_tmpl_id')
    def _onchange_attribute(self):
        product_attributes = self.product_tmpl_id.attribute_line_ids.mapped("attribute_id").mapped("id")
        product_values = self.product_tmpl_id.attribute_line_ids.mapped("value_ids").mapped("id")
        all_color_attributes = self.env["product.attribute"].search([("name", 'in', ['Color','color',"farbe",'Farbe'])]).mapped("id")

        color_attributes = intersection(product_attributes, all_color_attributes)
        return {
            'domain': {
                'original_value_id': [('attribute_id', 'in',color_attributes),('id', 'in', product_values)]
            }}

    original_value_id = fields.Many2one('product.attribute.value', string='Original Value')
    remapped_value_ids = fields.Many2many('product.attribute.value', string='Remapped Values')
    product_tmpl_id = fields.Many2one('product.template', string='Product', readonly=True, default=_compute_product)



# original_value_id moze da se zeme od produktot - so nekoj filter na imeto da sodzi
# color ili farbe ili sto ja znam
# i prethodno vo
# za domen kje gi stavam tie sto imaat parent (znaci deka se remapped)
#ili ednostavno da si kreira novi

