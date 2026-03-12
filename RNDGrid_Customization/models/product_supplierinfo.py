# -*- coding: utf-8 -*-
from odoo import models, fields

class SupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    price_student = fields.Float(
        'Student Price', default=0.0, required=True, digits='Product Price',
        help="The cost price from this Lab when the end customer is a Student."
    )
    price_startup = fields.Float(
        'Startup Price', default=0.0, required=True, digits='Product Price',
        help="The cost price from this Lab when the end customer is a Startup."
    )
    price_industry = fields.Float(
        'Industry Price', default=0.0, required=True, digits='Product Price',
        help="The cost price from this Lab when the end customer is from the Industry."
    )
