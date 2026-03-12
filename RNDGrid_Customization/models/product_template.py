# -*- coding: utf-8 -*-
from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    instrument_id = fields.Many2one('rndgrid.instrument', string='RNDGrid Instrument', help="The instrument used to perform this test.")

    def action_list_vendors(self):
        """
        Find Labs that support this product/test through their lab_instrument_ids
        and add them to the product's seller_ids list if they do not already exist.
        """
        for template in self:
            # Search for partners where:
            # 1. is_lab is True
            # 2. they have a lab_instrument_ids record where test_ids contains this template.id
            labs = self.env['res.partner'].search([
                ('is_lab', '=', True),
                ('lab_instrument_ids.test_ids', 'in', template.id)
            ])
            
            # Fetch existing vendors for this template
            existing_vendor_ids = template.seller_ids.mapped('partner_id.id')
            
            # Add Labs as new vendors if they aren't already listed
            new_sellers = []
            for lab in labs:
                if lab.id not in existing_vendor_ids:
                    # Append new product.supplierinfo dict for creation
                    new_sellers.append((0, 0, {
                        'partner_id': lab.id,
                        'min_qty': 1.0,
                    }))
            
            if new_sellers:
                template.write({'seller_ids': new_sellers})

