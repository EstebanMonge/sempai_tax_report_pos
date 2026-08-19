# -*- coding: utf-8 -*-

{
    'name': 'Sempai Tax Report for POS',
    'version': '15.0.1.0.0',
    'category': 'Reporting',
    'summary': 'Sempai tax PDF Reports for POS',
    'author': 'Sempai Space',
    'depends': [
        'base',
        'point_of_sale',
    ],
    'data': [
        'views/sempai_tax_report_wizard.xml',
        'report/sempai_tax_report_pos_template.xml',
        'report/sempai_tax_report_pos_report.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
