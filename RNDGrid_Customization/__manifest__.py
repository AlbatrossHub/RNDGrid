# -*- coding: utf-8 -*-
{
    'name': 'RNDGrid',
    'version': '1.0',
    'summary': 'Custom Addon for RNDGrid Labs and Instruments',
    'description': """
RNDGrid Customization
=====================
Manage Labs (vendors), Instruments, and specific pricing segments (Student, Startup, Industry).
- Extends res.partner to identify Labs and assign Customer Segments.
- Introduces rndgrid.instrument and rndgrid.lab.instrument to manage availability.
- Links product.template (Tests) to an Instrument.
- Extends product.supplierinfo for vendor cost price segments.
    """,
    'category': 'Customizations',
    'author': 'RNDGrid',
    'depends': ['base', 'contacts', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/rndgrid_menus.xml',
        'views/rndgrid_instrument_views.xml',
        'views/res_partner_views.xml',
        'views/product_template_views.xml',
        'views/product_supplierinfo_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
