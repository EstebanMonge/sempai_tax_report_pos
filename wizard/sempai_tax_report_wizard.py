# -*- coding: utf-8 -*-

import logging

from odoo import models, fields
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

    def action_print_report(self):

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

        return self.env.ref(
            'sempai_tax_report_pos.action_sempai_tax_report_pos'
        ).report_action(
            self,
            data={
                'pos_order_ids': pos_orders.ids,
                'date_start': self.date_start,
                'date_end': self.date_end,
            }
        )
