# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _get_rndgrid_sequence(self, date_order, company_id=False):
        if not date_order:
            date_order = fields.Datetime.now()
        elif isinstance(date_order, str):
            date_order = fields.Datetime.from_string(date_order)
            
        year = date_order.year
        if date_order.month < 4:
            fin_year = f"{str(year-1)[-2:]}-{str(year)[-2:]}"
        else:
            fin_year = f"{str(year)[-2:]}-{str(year+1)[-2:]}"
        
        company_id = company_id or self.env.company.id
        seq_code = f'sale.order.rndgrid.{fin_year}'
        
        Sequence = self.env['ir.sequence'].sudo().with_company(company_id)
        seq = Sequence.search([
            ('code', '=', seq_code),
            ('company_id', 'in', (company_id, False))
        ], limit=1)
        
        if not seq:
            seq = Sequence.create({
                'name': f'Sale Order RNDGrid {fin_year}',
                'code': seq_code,
                'padding': 5,
                'company_id': company_id,
            })
            
        next_num = seq._next()
        return f"QUO/{fin_year}/{next_num}", f"QUO/{fin_year}/"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                name, prefix = self._get_rndgrid_sequence(
                    vals.get('date_order'), 
                    vals.get('company_id')
                )
                vals['name'] = name
                
        return super(SaleOrder, self).create(vals_list)

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if 'date_order' in vals:
            for order in self:
                # Only update name if it's still a quotation and not _('New')
                if order.state in ('draft', 'sent') and order.name != _('New'):
                    name, prefix = self._get_rndgrid_sequence(
                        order.date_order, 
                        order.company_id.id
                    )
                    
                    # If the prefix isn't matching the new financial year, regenerate it
                    if not order.name.startswith(prefix):
                        order.name = name
        return res
