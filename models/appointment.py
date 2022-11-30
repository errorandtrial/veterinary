# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo import tools
from datetime import datetime
from odoo.exceptions import ValidationError, UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def app_id_auto(self):
        try:
            return self._context.get('active_ids')[0]
        except Exception:
            return False

    appointment_id = fields.Many2one('veterinary.appointment', default=lambda self: self.app_id_auto())


class Appointment(models.Model):
    _name = "veterinary.appointment"
    _order = "dateOfAppointment desc"
    name = fields.Char(string='Name', readonly=True, default=lambda self: _('New'))
    description = fields.Char('Description')
    partner_id = fields.Many2one('res.partner', string='Owner', required=True)
    dateOfAppointment = fields.Datetime('Date of Appointment', required=True)
    animals = fields.Many2many('veterinary.animal', string='Animals')
    evaluation_id = fields.One2many('veterinary.evaluation', 'name', string='Evaluation')
    telephone = fields.Char(related='partner_id.mobile')
    animal_id = fields.Many2one('veterinary.animal')
    user_id = fields.Many2one('res.users', string='Doctor', required=True, track_visibility='onchange',
                              default=lambda self: self.env.user)
    cancel_reason = fields.Text('Reason of cancellation')
    invoice_ids = fields.One2many('account.invoice', 'appointment_id', string="Appointment Id")
    total_invoiced = fields.Char('Total', compute='_total_count')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirm', 'Confirm'),
         ('done', 'Done'),
         ('cancel', 'Cancel')]
        , string='Status', index=True, default='draft',
        track_visibility='onchange', copy=False
    )

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('appointment.number') or _('New')
        res = super(Appointment, self).create(vals)
        return res

    @api.multi
    def _total_count(self):
        t = self.env['account.invoice'].search([['appointment_id', '=', self.id]])
        self.total_invoiced = len(t)

    @api.multi
    def action_cancel_appointment(self):
        return self.write({'state': 'cancel'})

    def invoice_view(self):
        action = self.env.ref('account.action_invoice_refund_out_tree')
        result = action.read()[0]
        result['domain'] = [('appointment_id', '=', self.id)]
        return result

    def _prepare_invoice_data(self, cr, uid, context=None):
        context = context or {}

        journal_obj = self.env['account.journal']

        if not self.partner_id:
            raise ValidationError(_('No Customer Defined!'),
                                 _("You must first select a Customer for Contract %s!") % self.name)

        fpos = False

        journal_ids = journal_obj.search([('type', '=', 'sale'),
                                                   ('company_id', '=', self.user_id.company_id.id or False)], limit=1)
        if not journal_ids:
            raise ValidationError(_('Error!'),
                                 _('Please define a sale journal for the company "%s".') % (
                                 self.user_id.company_id.name or '',))

        property_payment_term = self.env['account.payment.term']
        partner_payment_term = property_payment_term.search([], limit=1)

        if self.partner_id.property_product_pricelist:
            currency_id = self.partner_id.property_product_pricelist.currency_id.id
        elif self.user_id.company_id:
            currency_id = self.user_id.company_id.currency_id.id

        invoice = {
            'account_id': self.partner_id.property_account_payable_id.id,
            'type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'currency_id': currency_id,
            'journal_id': len(journal_ids) and journal_ids[0] or False,
            'date_invoice': datetime.today(),
            'origin': self.name,
            'fiscal_position': fpos and fpos.id,
            'payment_term': partner_payment_term,
            'company_id': self.user_id.company_id.id or False,
        }
        return invoice

    def _prepare_invoice_lines(self, cr, uid, fiscal_position_id, context=None):
        fpos_obj = self.pool.get('account.fiscal.position')
        fiscal_position = None
        if fiscal_position_id:
            fiscal_position = fpos_obj.browse(cr, uid, fiscal_position_id, context=context)
        invoice_lines = []
        # for line in contract.recurring_invoice_line_ids:
        #
        #     res = line.product_id
        #     account_id = res.property_account_income.id
        #     if not account_id:
        #         account_id = res.categ_id.property_account_income_categ.id
        #     account_id = fpos_obj.map_account(cr, uid, fiscal_position, account_id)
        #
        #     taxes = res.taxes_id or False
        #     tax_id = fpos_obj.map_tax(cr, uid, fiscal_position, taxes)
        #
        #     invoice_lines.append((0, 0, {
        #         'name': line.name,
        #         'account_id': account_id,
        #         'account_analytic_id': contract.id,
        #         'price_unit': line.price_unit or 0.0,
        #         'quantity': line.quantity,
        #         'uos_id': line.uom_id.id or False,
        #         'product_id': line.product_id.id or False,
        #         'invoice_line_tax_id': [(6, 0, tax_id)],
        #     }))
        return invoice_lines

    def _prepare_invoice(self, cr, uid, context=None):
        invoice = self._prepare_invoice_data(cr, uid,  context)
        invoice['invoice_line'] = self._prepare_invoice_lines(cr, uid, invoice['fiscal_position'], context)
        return invoice

    @api.one
    def action_confirm(self):
        self.state = 'confirm'
        for animal in self.animals:
            pick = {
                'animal': animal.id,
                'appointment_id': self.id,
                'partner_id': self.partner_id.id,
            }
            picking = self.env['veterinary.evaluation'].create(pick)
        return self.invoice_view()

    @api.one
    def action_create_invoice(self, grouped=False, final=False):
        inv_obj = self.env['account.invoice']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoice = self._prepare_invoice(self, self.env.cr, self.env.uid)
        references = {}
        invoices_origin = {}
        invoices_name = {}

        # for appointment in self:
        #     group_key = appointment.id
        #     for line in appointment.evaluation_id.prescriptions.sorted(key=lambda l: l.qty_to_invoice < 0):
        #         if float_is_zero(line.qty_to_invoice, precision_digits=precision):
        #             continue
        #         if line.qty_to_invoice > 0:
        #             line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)
        #         elif line.qty_to_invoice < 0 and final:
        #             line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)
        #
        # for group_key in invoices:
        #     invoices[group_key].write({'name': ', '.join(invoices_name[group_key]),
        #                                'origin': ', '.join(invoices_origin[group_key])})
        #
        # if not invoices:
        #     raise UserError(_('There is no invoiceable line.'))

        invoice.compute_taxes()
        if not invoice.invoice_line_ids:
            raise UserError(_('There is no invoiceable line.'))
        # If invoice is negative, do a refund invoice instead
        if invoice.amount_total < 0:
            invoice.type = 'out_refund'
            for line in invoice.invoice_line_ids:
                line.quantity = -line.quantity
        # Use additional field helper function (for account extensions)
        for line in invoice.invoice_line_ids:
            line._set_additional_fields(invoice)
        # Necessary to force computation of taxes and cash rounding. In account_invoice, they are triggered
        # by onchanges, which are not triggered when doing a create.
        invoice.compute_taxes()
        invoice._onchange_cash_rounding()
        invoice.message_post_with_view('mail.message_origin_link',
                                       values={'self': invoice, 'origin': references[invoice]},
                                       subtype_id=self.env.ref('mail.mt_note').id)
        return [invoice.id]

    @api.one
    def action_done(self):
        self.state = 'done'
