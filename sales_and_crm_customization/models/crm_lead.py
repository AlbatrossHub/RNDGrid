# -*- coding: utf-8 -*-
from odoo import models, fields

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    rndgrid_material_name = fields.Char(string='Material Name')
    rndgrid_segment = fields.Selection(
        related='partner_id.rndgrid_segment',
        string='Segment',
        readonly=True,
    )
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

    def _prepare_opportunity_quotation_context(self):
        """ Override to auto-populate sale.order.lines with the requested tests """
        quotation_context = super(CrmLead, self)._prepare_opportunity_quotation_context()
        
        # Build the default order lines from the requested tests
        order_lines = []
        for line in self.rndgrid_test_line_ids:
            for test in line.test_ids:
                order_lines.append((0, 0, {
                    'product_id': test.product_variant_id.id,
                    'product_template_id': test.id,
                    'name': test.name,
                    'product_uom_qty': 1.0,
                    'rndgrid_instrument_id': line.instrument_id.id,
                }))
        
        if order_lines:
            quotation_context['default_order_line'] = order_lines
            
        return quotation_context


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
