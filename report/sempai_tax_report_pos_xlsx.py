# -*- coding: utf-8 -*-

from odoo import models


class SempaiTaxReportPosXlsx(models.AbstractModel):
    _name = 'report.sempai_tax_report_pos.sempai_tax_report_pos_xlsx'
    _description = 'Sempai Space POS Tax Report (Excel)'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizards):

        values = self.env[
            'sempai.tax.report.pos.wizard'
        ]._compute_report_values(data)

        sheet = workbook.add_worksheet('POS Tax Report')

        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
        })

        section_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'top': 1,
        })

        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D9D9D9',
            'border': 1,
        })

        text_format = workbook.add_format({
            'border': 1,
        })

        money_format = workbook.add_format({
            'border': 1,
            'num_format': '#,##0.00',
        })

        total_label_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'right',
        })

        total_money_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'num_format': '#,##0.00',
        })

        sheet.set_column('A:A', 22)
        sheet.set_column('B:B', 14)
        sheet.set_column('C:C', 30)
        sheet.set_column('D:F', 16)

        row = 0

        sheet.write(row, 0, 'Sempai Tax Report - POS', title_format)
        row += 2

        sheet.write(row, 0, 'Start Date:')
        sheet.write(row, 1, str(values['date_start'] or ''))
        row += 1

        sheet.write(row, 0, 'End Date:')
        sheet.write(row, 1, str(values['date_end'] or ''))
        row += 2

        # ============================================================
        # SALES
        # ============================================================

        sheet.write(row, 0, 'Sales', section_format)
        row += 1

        for col, header in enumerate(
            ['Invoice', 'Date', 'Partner', 'Subtotal', 'Taxes', 'Total']
        ):
            sheet.write(row, col, header, header_format)
        row += 1

        for order in values['pos_orders']:

            sheet.write(row, 0, order.name or '', text_format)
            sheet.write(row, 1, str(order.date_order or ''), text_format)
            sheet.write(
                row, 2,
                order.partner_id.display_name if order.partner_id else '',
                text_format,
            )
            sheet.write(
                row, 3,
                order.amount_total - order.amount_tax,
                money_format,
            )
            sheet.write(row, 4, order.amount_tax, money_format)
            sheet.write(row, 5, order.amount_total, money_format)
            row += 1

        sheet.merge_range(
            row, 0, row, 2, 'Total Sales', total_label_format
        )
        sheet.write(row, 3, values['sales_subtotal'], total_money_format)
        sheet.write(row, 4, values['sales_tax'], total_money_format)
        sheet.write(row, 5, values['sales_total'], total_money_format)
        row += 3

        # ============================================================
        # SALES TAX SUMMARY
        # ============================================================

        sheet.write(row, 0, 'Sales Tax Summary', section_format)
        row += 1

        for col, header in enumerate(
            ['Tax Group', 'Subtotal', 'Tax', 'Total']
        ):
            sheet.write(row, col, header, header_format)
        row += 1

        for tax_group in values['tax_groups'].values():
            sheet.write(row, 0, tax_group['name'], text_format)
            sheet.write(row, 1, tax_group['subtotal'], money_format)
            sheet.write(row, 2, tax_group['tax'], money_format)
            sheet.write(row, 3, tax_group['total'], money_format)
            row += 1
