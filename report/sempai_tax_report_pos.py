# -*- coding: utf-8 -*-

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class SempaiTaxReport(models.AbstractModel):
    _name = 'report.sempai_tax_report_pos.sempai_tax_report_pos_document'

    @api.model
    def _get_report_values(self, docids, data=None):

        data = data or {}

        pos_order_ids = data.get('pos_order_ids', [])
        date_start = data.get('date_start')
        date_end = data.get('date_end')

        # ============================================================
        # POS ORDERS
        # ============================================================

        pos_orders = self.env['pos.order'].browse(
            pos_order_ids
        ).sorted(
            key=lambda order: (
                order.partner_id.name or '',
                order.date_order or '',
            )
        )

        # ============================================================
        # POS SALES TOTALS
        # ============================================================


        sales_subtotal = round(
            sum(
                order.amount_total - order.amount_tax
                for order in pos_orders
            ),
            2
        )


        sales_tax = round(
            sum(
                order.amount_tax
                for order in pos_orders
            ),
            2
        )


        sales_total = round(
            sum(
                order.amount_total
                for order in pos_orders
            ),
            2
        )


        _logger.info(
            'POS SALES TOTALS | Subtotal=%s | Tax=%s | Total=%s',
            sales_subtotal,
            sales_tax,
            sales_total,
        )

        # ============================================================
        # POS TAX GROUP CALCULATION
        # ============================================================

        tax_groups = {}

        for order in pos_orders:

            for line in order.lines:

                # POS order line taxes
                for tax in line.tax_ids:

                    tax_group = tax.tax_group_id

                    if not tax_group:
                        continue

                    group_id = tax_group.id

                    if group_id not in tax_groups:
                        tax_groups[group_id] = {
                            'name': tax_group.name,
                            'subtotal': 0.0,
                            'tax': 0.0,
                            'total': 0.0,
                        }

                    # ------------------------------------------------
                    # Calculate tax using the POS line values
                    # ------------------------------------------------

                    price = line.price_unit * (
                        1 - (line.discount or 0.0) / 100.0
                    )

                    taxes = tax.compute_all(
                        price,
                        order.pricelist_id.currency_id,
                        line.qty,
                        product=line.product_id,
                        partner=order.partner_id,
                    )

                    for tax_value in taxes['taxes']:

                        if tax_value['id'] != tax.id:
                            continue

                        tax_amount = tax_value['amount']
                        tax_base = tax_value['base']

                        tax_groups[group_id]['subtotal'] += tax_base
                        tax_groups[group_id]['tax'] += tax_amount
                        tax_groups[group_id]['total'] += (
                            tax_base + tax_amount
                        )

        # ============================================================
        # TAX GROUP LOG
        # ============================================================

        _logger.info(
            '============================================================'
        )

        _logger.info(
            'POS TAX GROUP SUMMARY'
        )

        for group_id, values in tax_groups.items():

            _logger.info(
                'POS Tax Group ID=%s | Name=%s | Subtotal=%s | '
                'Tax=%s | Total=%s',
                group_id,
                values['name'],
                values['subtotal'],
                values['tax'],
                values['total'],
            )

        _logger.info(
            '============================================================'
        )

        # ============================================================
        # REPORT DATA LOG
        # ============================================================

        _logger.info(
            'POS REPORT DATA'
        )

        _logger.info(
            'POS Order IDs: %s',
            pos_order_ids,
        )

        _logger.info(
            'Date range: %s -> %s',
            date_start,
            date_end,
        )

        _logger.info(
            'POS orders found in report: %s',
            len(pos_orders),
        )

        for order in pos_orders:

            _logger.info(
                'REPORT POS Order ID=%s | Name=%s | Date=%s | '
                'Partner=%s | State=%s | Tributacion=%s | '
                'Amount Tax=%s | Amount Total=%s',
                order.id,
                order.name,
                order.date_order,
                order.partner_id.display_name
                if order.partner_id else '',
                order.state,
                order.state_tributacion,
                order.amount_tax,
                order.amount_total,
            )

        _logger.info(
            '============================================================'
        )

        # ============================================================
        # REPORT VALUES
        # ============================================================

        return {
            'doc_ids': docids,
            'doc_model': 'sempai.tax.report.pos.wizard',

            'docs': self.env[
                'sempai.tax.report.pos.wizard'
            ].browse(docids),

            'pos_orders': pos_orders,

            'date_start': date_start,
            'date_end': date_end,

            'sales_subtotal': sales_subtotal,
            'sales_tax': sales_tax,
            'sales_total': sales_total,

            'tax_groups': tax_groups,
        }
