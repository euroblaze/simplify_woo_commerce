# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductAttributeReMap(models.Model):
    _name = 'product.attribute.remap'

    def _compute_product(self):
        return self._context.get("product_id")

    @api.onchange('product_tmpl_id')
    def _onchange_attribute(self):
        print("self",  self.__dict__)

    original_value_id = fields.Many2one('product.attribute.value', string='Original Value')
    remapped_value_ids = fields.Many2many('product.attribute.value', string='Remapped Values')
    product_tmpl_id = fields.Many2one('product.template', string='Product', readonly=True, default=_compute_product)



# original_value_id moze da se zeme od produktot - so nekoj filter na imeto da sodzi
# color ili farbe ili sto ja znam
# i prethodno vo
# za domen kje gi stavam tie sto imaat parent (znaci deka se remapped)
#ili ednostavno da si kreira novi

