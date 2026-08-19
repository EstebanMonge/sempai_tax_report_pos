# -*- coding: utf-8 -*-

{
    'name': 'Sempai Tax Report for POS',
    'version': '12.0.1.0.0',
    'category': 'Reporting',
    'summary': 'Sempai tax PDF Reports for POS',
    'author': 'Sempai Space',
    'depends': [
        'base',
    ],
    'data': [
        'views/sempai_tax_report_wizard.xml',
        'report/sempai_tax_report_pos_template.xml',
        'report/sempai_tax_report_pos_report.xml',
    ],
    'installable': True,
    'application': False,
}
