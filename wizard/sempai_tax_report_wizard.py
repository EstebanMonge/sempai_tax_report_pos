# -*- coding: utf-8 -*-

import logging

from odoo import api, models, fields
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SempaiTaxReportWizard(models.TransientModel):
    _name = 'sempai.tax.report.pos.wizard'
    _description = 'Sempai Tax Report Wizard for POS'

    date_start = fields.Date(
        string='Start Date',
        required=True,
    )

    date_end = fields.Date(
        string='End Date',
        required=True,
    )

    def _get_report_data(self):

        self.ensure_one()

        if self.date_start and self.date_end:
            if self.date_start > self.date_end:
                raise ValidationError(
                    'Start Date cannot be greater than End Date.'
                )
        company = self.env.user.company_id

        pos_domain = [
            ('company_id', '=', company.id),
            ('date_order', '>=', self.date_start),
            ('date_order', '<=', self.date_end),
            ('state', '=', 'done'),
        ]

        # Simplified regimen companies (electronic invoicing disabled)
        # never populate state_tributacion, so it must not be used to
        # filter their POS orders.
        if company.frm_ws_ambiente != 'disabled':
            pos_domain.append(('state_tributacion', '=', 'aceptado'))

        pos_orders = self.env['pos.order'].search(pos_domain).sorted(
            key=lambda order: (
                order.partner_id.name or '',
                order.date_order or '',
            )
        )

        _logger.info(
            '============================================================'
        )
        _logger.info(
            'SEMPAI TAX REPORT POS - POS ORDER SEARCH'
        )
        _logger.info(
            'Company ID: %s',
            company.id,
        )
        _logger.info(
            'Company: %s',
            company.name,
        )
        _logger.info(
            'Date range: %s -> %s',
            self.date_start,
            self.date_end,
        )
        _logger.info(
            'POS orders found: %s',
            len(pos_orders),
        )

        for order in pos_orders:
            _logger.info(
                'POS Order ID=%s | Name=%s | Date=%s | Partner=%s | '
                'State=%s | Tributacion=%s | Electronic Number=%s | '
                'Amount Tax=%s | Amount Total=%s',
                order.id,
                order.name,
                order.date_order,
                order.partner_id.display_name
                if order.partner_id else '',
                order.state,
                order.state_tributacion,
                order.number_electronic,
                order.amount_tax,
                order.amount_total,
            )

        _logger.info(
            '============================================================'
        )

        return {
            'pos_order_ids': pos_orders.ids,
            'date_start': self.date_start,
            'date_end': self.date_end,
        }

    def action_print_report(self):

        data = self._get_report_data()

        return self.env.ref(
            'sempai_tax_report_pos.action_sempai_tax_report_pos'
        ).report_action(self, data=data)

    def action_export_xlsx(self):

        data = self._get_report_data()

        return self.env.ref(
            'sempai_tax_report_pos.action_sempai_tax_report_pos_xlsx'
        ).report_action(self, data=data)

    @api.model
    def _compute_report_values(self, data):
        """Shared computation used by both the PDF and Excel renders."""

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

                    taxes = tax.compute_all(
                        line.price_unit,
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
        # POS SALES TOTALS
        # ============================================================

        sales_subtotal = sum(
            order.amount_total - order.amount_tax
            for order in pos_orders
        )

        sales_tax = sum(
            order.amount_tax
            for order in pos_orders
        )

        sales_total = sum(
            order.amount_total
            for order in pos_orders
        )

        _logger.info(
            'POS SALES TOTALS | Subtotal=%s | Tax=%s | Total=%s',
            sales_subtotal,
            sales_tax,
            sales_total,
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

        return {
            'pos_orders': pos_orders,

            'date_start': date_start,
            'date_end': date_end,

            'sales_subtotal': sales_subtotal,
            'sales_tax': sales_tax,
            'sales_total': sales_total,

            'tax_groups': tax_groups,
        }
