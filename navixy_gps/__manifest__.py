# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Navixy GPS",
    'version': '1.0',
    'depends': [
        'l10n_mn_technic'
    ],
    'author': "Tsengel",
    'category': 'Hidden',
    'description': """
         Navixy GPS integration module
    """,
    'data': [
        'views/technic_views.xml',
        'views/stop_report_views.xml',
        'views/gps_views.xml',
        'data/ir_cron.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
