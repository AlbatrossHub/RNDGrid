# -*- coding: utf-8 -*-
from odoo import models, fields

class RndGridInstrument(models.Model):
    _name = 'rndgrid.instrument'
    _description = 'RNDGrid Instrument'

    name = fields.Char(string='Instrument Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True, string='Active')


class RndGridLabInstrument(models.Model):
    _name = 'rndgrid.lab.instrument'
    _description = 'RNDGrid Lab Instrument Configuration'

    lab_id = fields.Many2one('res.partner', string='Lab', ondelete='cascade', required=True, domain=[('is_lab', '=', True)])
    instrument_id = fields.Many2one('rndgrid.instrument', string='Instrument', ondelete='cascade', required=True)
    test_ids = fields.Many2many(
        'product.template', 
        string='Available Tests',
        domain="[('instrument_id', '=', instrument_id)]",
        help="The specific tests this Lab can perform with this Instrument."
    )
