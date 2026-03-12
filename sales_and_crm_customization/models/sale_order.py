# -*- coding: utf-8 -*-
from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    rndgrid_segment = fields.Selection(
        related='partner_id.rndgrid_segment',
        string='User Type',
        readonly=True,
    )
