# -*- coding: utf-8 -*-
from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    instrument_id = fields.Many2one('rndgrid.instrument', string='RNDGrid Instrument', help="The instrument used to perform this test.")
