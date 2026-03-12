# -*- coding: utf-8 -*-
from odoo import models, fields, api

class RndGridVendorSelectorWizard(models.TransientModel):
    _name = 'rndgrid.vendor.selector.wizard'
    _description = 'Select Lab Vendor Wizard'

    line_id = fields.Many2one('sale.order.line', string='Sale Order Line')
    product_tmpl_id = fields.Many2one('product.template', string='Test (Product)')
    vendor_line_ids = fields.One2many(
        'rndgrid.vendor.selector.wizard.line', 'wizard_id', 
        string='Available Vendors'
    )

class RndGridVendorSelectorWizardLine(models.TransientModel):
    _name = 'rndgrid.vendor.selector.wizard.line'
    _description = 'Select Lab Vendor Wizard Line'

    wizard_id = fields.Many2one('rndgrid.vendor.selector.wizard', string='Wizard')
    partner_id = fields.Many2one('res.partner', string='Lab (Vendor)')
    price_student = fields.Monetary(string='Student Price', currency_field='currency_id')
    price_startup = fields.Monetary(string='Startup Price', currency_field='currency_id')
    price_industry = fields.Monetary(string='Industry Price', currency_field='currency_id')
    currency_id = fields.Many2one(related='partner_id.currency_id', depends=['partner_id'])

    def action_select_vendor(self):
        self.ensure_one()
        line = self.wizard_id.line_id
        if line:
            line.rndgrid_lab_id = self.partner_id
            
            # Determine cost based on customer segment
            segment = line.order_id.partner_id.rndgrid_segment
            if segment == 'student':
                cost = self.price_student
            elif segment == 'startup':
                cost = self.price_startup
            elif segment == 'industry':
                cost = self.price_industry
            else:
                cost = 0.0 # Default if no segment
                
            line.rndgrid_cost = cost
                
        return {'type': 'ir.actions.act_window_close'}
