{
    'name': "Navixy GPS",
    'version': '1.0',
    'depends': [
        'l10n_mn_technic', 'stock',
    ],

    'author': "Tsengel",
    'category': 'Hidden',
    'description': """
         Navixy GPS integration module
    """,
    'data': [
        'views/gps_views.xml',
        'views/technic_views.xml',
        'views/stop_report_views.xml',
        'views/zone_report_views.xml',
        'views/fuel_report_views.xml',
        'views/motohour_report_views.xml',
        'report/fuel_report_analyze_view.xml',
        'data/ir_cron.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
