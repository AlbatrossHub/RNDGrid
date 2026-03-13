# -*- coding: utf-8 -*-

from odoo import models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('tz') == 'Asia/Calcutta':
                vals['tz'] = 'Asia/Kolkata'
        return super(ResPartner, self).create(vals_list)

    def write(self, vals):
        if vals.get('tz') == 'Asia/Calcutta':
            vals['tz'] = 'Asia/Kolkata'
        return super(ResPartner, self).write(vals)
