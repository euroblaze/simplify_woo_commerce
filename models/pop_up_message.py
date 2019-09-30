# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CustomPopUpMessage(models.TransientModel):
    _name = 'custom.pop.up.message'

    message = fields.Char(string='Info message')

