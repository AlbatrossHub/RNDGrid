# -*- coding: utf-8 -*-
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_lab = fields.Boolean(string='Is Lab', default=False, help="Check this box if this contact is a testing Lab.", Tracking=True)
    
    rndgrid_segment = fields.Selection([
        ('academia', 'Academia'),
        ('startup', 'Startup'),
        ('industry', 'Industry')
    ], string='User Type', help="Segment used for specific pricing rules.", Tracking=True)

    lab_instrument_ids = fields.One2many(
        'rndgrid.lab.instrument', 'lab_id', 
        string='Lab Instruments',
        help="Instruments available at this lab."
    )
    institute_name = fields.Char(string="Institute Name", Tracking=True)
