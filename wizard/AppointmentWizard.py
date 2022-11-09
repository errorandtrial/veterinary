
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning

class AppointmentConfirm(models.TransientModel):
    """
    This wizard will confirm the all the selected draft appointment
    """

    _name = "veterinary.appointment.confirm"
    _description = "Confirm the selected Appointments"

    @api.multi
    def appointment_confirm(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['veterinary.appointment'].browse(active_ids):
            if record.state not in ('draft'):
                raise UserError(_("Selected appointment(s) cannot be confirmed as they are not in 'Draft' state."))
            record.action_confirm()
        return {'type': 'ir.actions.act_window_close'}

class CancelAppointment(models.TransientModel):
    _name = "cancel.appoint.wizard"
    
    reason = fields.Text('Cancel Reason', required=True)
    @api.multi
    def action_cancel_appointment(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for record in self.env['veterinary.appointment'].browse(active_ids):
            record.cancel_reason = self.reason
            record.state = 'cancel'
        return {'type': 'ir.actions.act_window_close'}
