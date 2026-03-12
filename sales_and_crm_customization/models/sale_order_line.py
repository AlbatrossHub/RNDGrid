# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    rndgrid_instrument_id = fields.Many2one(
        'rndgrid.instrument', 
        string='Instrument', 
        help="The instrument used to perform this test."
    )
    rndgrid_lab_id = fields.Many2one(
        'res.partner', 
        string='Lab',
        domain="[('is_lab', '=', True)]",
        help="The lab assigned to perform this test."
    )
    rndgrid_cost = fields.Monetary(
        string='Cost',
        help="The cost price of this test from the assigned lab based on the customer's segment."
    )

    @api.onchange('product_template_id', 'product_id')
    def _onchange_product_id_set_instrument(self):
        for line in self:
            # product_template_id exists in newer Odoo versions on sale.order.line, 
            # but usually product_id is the standard fallback.
            product_tmpl = line.product_template_id or getattr(line.product_id, 'product_tmpl_id', False)
            if product_tmpl and product_tmpl.instrument_id:
                line.rndgrid_instrument_id = product_tmpl.instrument_id

    def view_available_vendors(self):
        self.ensure_one()
        product_tmpl = self.product_template_id or getattr(self.product_id, 'product_tmpl_id', False)
        
        if not product_tmpl:
            return

        # Find all supplier info records for this product
        supplier_infos = self.env['product.supplierinfo'].search([
            ('product_tmpl_id', '=', product_tmpl.id)
        ])

        # Prepare wizard lines
        vendor_lines = [(0, 0, {
            'partner_id': supplier.partner_id.id,
            'price_student': supplier.price_student,
            'price_startup': supplier.price_startup,
            'price_industry': supplier.price_industry,
        }) for supplier in supplier_infos if supplier.partner_id.is_lab]

        wizard = self.env['rndgrid.vendor.selector.wizard'].create({
            'line_id': self.id,
            'product_tmpl_id': product_tmpl.id,
            'vendor_line_ids': vendor_lines
        })

        return {
            'name': 'Select Available Vendor',
            'type': 'ir.actions.act_window',
            'res_model': 'rndgrid.vendor.selector.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }
