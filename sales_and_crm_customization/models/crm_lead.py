# -*- coding: utf-8 -*-
from odoo import models, fields

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    rndgrid_material_name = fields.Char(string='Material Name')
    rndgrid_sample_type = fields.Selection([
        ('liquid', 'Liquid'),
        ('solid', 'Solid'),
        ('powder', 'Powder'),
        ('thin_film', 'Thin Film'),
        ('nanomaterial', 'NanoMaterial'),
        ('biological', 'Biological Sample'),
        ('polymer', 'Polymer / Plastic'),
        ('metal', 'Metal/Alloy'),
        ('composite', 'Composite / Ceramic'),
        ('coated_surface', 'Coated Surface'),
        ('other', 'Other')
    ], string='Sample Type')
    rndgrid_is_hazardous = fields.Boolean(string='Is this sample hazardous?', default=False)
    rndgrid_test_line_ids = fields.One2many(
        'crm.lead.rndgrid.test', 'lead_id', 
        string='Requested Tests'
    )


class CrmLeadRndGridTest(models.Model):
    _name = 'crm.lead.rndgrid.test'
    _description = 'CRM Lead Requested Test'

    lead_id = fields.Many2one('crm.lead', string='Lead', ondelete='cascade', required=True)
    instrument_id = fields.Many2one('rndgrid.instrument', string='Instrument', required=True)
    test_ids = fields.Many2many(
        'product.template', 
        string='Tests Needed',
        domain="[('instrument_id', '=', instrument_id)]",
        help="Which specific tests are required using this instrument?"
    )
