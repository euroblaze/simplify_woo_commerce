# -*- coding: utf-8 -*-
from odoo import models, fields, api

class InhertSaleOrder(models.Model):
    _inherit = 'sale.order'

    woo_order_number = fields.Integer(string='Woo Order Number')
    woo_order_key = fields.Char(string='Woo Order key')


    # @api.model
    # def create(self,vals):
    #     res = super(InhertSaleOrder,self).create(vals)
    #     res.action_confirm()
    #     return res

    # @api.multi
    # def write(self, values):
    #     res = super(InhertSaleOrder, self).write(values)
    #     res.action_confirm()
    #     return res


