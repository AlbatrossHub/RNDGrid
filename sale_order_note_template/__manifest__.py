{
    'name': 'Sale Orders Terms and conditions Templates',
    'version': '1.0',
    'summary': """Add sale orders terms and conditions template that can be""",
    'category': 'Sales',
    'depends': ['sale_management'],
    'data': [
        "views/sale_terms_template.xml",
        "views/sale_views.xml",
        "report/sale_report_templates.xml",
        "security/ir.model.access.csv",
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
