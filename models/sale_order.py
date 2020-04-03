# -*- coding: utf-8 -*-
from odoo import models, fields, api


class InhertSaleOrder(models.Model):
    _inherit = 'sale.order'

    woo_order_number = fields.Integer(string='Woo Order Number')
    woo_order_key = fields.Char(string='Woo Order key')
    woo_order_status = fields.Selection([('pending', 'Pending Payment'),
                                         ('processing', 'Processing'),
                                         ('on-hold', 'On hold'),
                                         ('completed', 'Completed'),
                                         ('cancelled', 'Cancelled'),
                                         ('refunded', 'Refunded'),
                                         ('failed', 'Failed'),
                                         ('trash', 'Trash')
                                         ],
                                        default='pending',
                                        description="Order status. Options: pending, processing, on-hold, completed, "
                                                    "cancelled, refunded, failed and trash. Default is pending"
                                        )

    def _compute_pos(self):
        if self.channel_id:
            self.pos = self.channel_id.pos
            print("POS", self.pos)

    pos = fields.Integer(string='Channel pos', compute=_compute_pos, readonly=True)

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
