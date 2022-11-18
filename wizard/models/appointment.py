# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo import tools

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    def app_id_auto(self):
        try:
            return self._context.get('active_ids')[0]
        except Exception:
            return False
    appointment_id = fields.Many2one('veterinary.appointment',default=lambda self: self.app_id_auto()  )

class Appointment(models.Model):
    _name = "veterinary.appointment"
    _order = "dateOfAppointment desc"
    name = fields.Char(string='Name',readonly=True,default=lambda self: _('New'))
    description = fields.Char('Description')
    partner_id = fields.Many2one('res.partner',string='Owner',required=True)
    dateOfAppointment = fields.Datetime('Date of Appointment',required=True)
    animals = fields.Many2many('veterinary.animal',string='Animals')
    animal_id = fields.Many2one('veterinary.animal')
    user_id = fields.Many2one('res.users', string='Doctor',required=True,track_visibility='onchange',default=lambda self: self.env.user)
    cancel_reason = fields.Text('Reason of cancellation')
    invoice_ids = fields.One2many('account.invoice','appointment_id', string="Appointment Id")
    total_invoiced = fields.Char('Total',compute='_total_count')
    state = fields.Selection(
        [('draft','Draft'),
        ('confirm','Confirm'),
        ('cancel','Cancel')]
        , string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False
    )
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('appointment.number') or _('New')
        res = super(Appointment, self).create(vals)
        return res
    
    @api.multi
    def action_create_invoice(self):
        for appointment in self:
            inv = {
            'appointment_id': appointment.id,
            'partner_id': appointment.partner_id.id,
            }
            invoiced = self.env['account.invoice'].create(inv)
    
    @api.multi
    def _total_count(self):
        t = self.env['account.invoice'].search([['appointment_id','=',self.id]])
        self.total_invoiced  = len(t)
    
    @api.multi
    def action_cancel_appointment(self):
        return self.write({'state': 'cancel'})
    
    def invoice_view(self):
        action = self.env.ref('account.action_invoice_refund_out_tree')
        result = action.read()[0]
        result['domain'] = [('appointment_id', '=', self.id)]
        return result
    
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
    
