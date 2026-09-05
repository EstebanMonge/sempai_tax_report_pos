# -*- coding: utf-8 -*-

from odoo import api, models


class SempaiTaxReport(models.AbstractModel):
    _name = 'report.sempai_tax_report_pos.sempai_tax_report_pos_document'

    @api.model
    def _get_report_values(self, docids, data=None):

        values = self.env[
            'sempai.tax.report.pos.wizard'
        ]._compute_report_values(data)

        values.update({
            'doc_ids': docids,
            'doc_model': 'sempai.tax.report.pos.wizard',

            'docs': self.env[
                'sempai.tax.report.pos.wizard'
            ].browse(
                (data or {}).get('context', {}).get('active_ids', [])
            ),
        })

        return values
