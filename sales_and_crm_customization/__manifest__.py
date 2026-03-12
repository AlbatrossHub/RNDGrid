# -*- coding: utf-8 -*-
{
    'name': 'Sales & CRM Customization',
    'version': '1.0',
    'summary': 'Custom Addon for RNDGrid CRM Lead requirements',
    'description': """
Sales and CRM Customization
===========================
Captures specific sample and testing requirements directly on the CRM Lead.
- Material Name
- Sample Type
- Is Hazardous?
- Tests Needed (Mapping to RNDGrid Instruments and Tests)
    """,
    'category': 'Sales/CRM',
    'author': 'RNDGrid',
    'depends': ['crm', 'sale_management', 'sale_crm', 'RNDGrid_Customization'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/rndgrid_vendor_selector_wizard_views.xml',
        'views/crm_lead_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
