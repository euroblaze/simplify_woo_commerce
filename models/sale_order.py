# -*- coding: utf-8 -*-
from odoo import models, fields, api


class InheritSaleOrder(models.Model):
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
    woo_order_id = fields.Integer(string="Woo Order ID")

    def _compute_pos(self):
        if self.channel_id:
            self.pos = self.channel_id.pos
            print("POS", self.pos)

    pos = fields.Integer(string='Channel pos', compute=_compute_pos, readonly=True)

    def export_woo_order_status(self):
        print("Status exported")
        print(self)
        order = self
        if int(order.channel_id.pos) == 3:
            print("Woo Order")
            woo_id = order.woo_order_id
            data = {}
            wcapi = order.channel_id.create_woo_commerce_object()
            data['status'] = order.woo_order_status
            # print("Woo Order ID", order.woo_order_id)
            wcapi.put("orders/%s" % (woo_id), data).json()
