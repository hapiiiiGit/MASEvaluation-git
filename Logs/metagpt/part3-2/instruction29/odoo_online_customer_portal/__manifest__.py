# -*- coding: utf-8 -*-
{
    'name': 'Odoo Online Customer Portal',
    'summary': 'Redesigned customer portal with modern UI and legal compliance features',
    'version': '1.0.0',
    'category': 'Website',
    'author': 'Your Company',
    'website': 'https://yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'website',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/portal_templates.xml',
        'views/admin_consent_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'odoo_online_customer_portal/static/src/scss/portal.scss',
            'odoo_online_customer_portal/static/src/js/portal.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'description': """
Odoo Online Customer Portal
==========================
- Modern UI redesign using QWeb, SCSS, and JS
- Terms & Conditions checkbox on registration and relevant forms
- Customer consent storage and audit trail
- Admin consent management panel
- GDPR and legal compliance features
""",
}