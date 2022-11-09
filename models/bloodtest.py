# -*- coding: utf-8 -*-

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang

   
class BloodTest(models.Model):
    _name = 'veterinary.bloodtest'
    _inherit = ['mail.thread']     
    _order = "dateOfAppointment desc"
    name = fields.Char(string='Test ID', required=True, copy=False, readonly=True,index=True, default=lambda self: _('New'))
    animal = fields.Many2one('veterinary.animal')
    owner_id = fields.Many2one('res.partner', string='Owner', required=True)
    appointment_id = fields.Many2one('veterinary.appointment',string='Appointment',required=True)
    date = fields.Datetime(string='Date', related='appointment_id.dateOfAppointment')
    user_id = fields.Many2one('res.users', string='Doctor')
    hematies = fields.Float('Hematíes')
    platellets = fields.Float('Plaquetas')
    neutro = fields.Float('Neutrófilos')
    linfo = fields.Float('Linfocitos')
    other_bt = fields.Text('Other')
    overall_assessment_bt = fields.Text('Overall Assessment')
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('increment_test') or _('New')
        res = super(BloodTest, self).create(vals)
        return res

    
    # @api.multi
    # def action_analitica_sent(self):
    #     '''
    #     This function opens a window to compose an email, with the edi sale template message loaded by default
    #     '''
    #     self.ensure_one()
    #     ir_model_data = self.env['ir.model.data']
    #     try:
    #         template_id = ir_model_data.get_object_reference('veterinary', 'email_template_edi_sale')[1]
    #     except ValueError:
    #         template_id = False       
    #     ctx = {
    #         'default_model': 'veterinary.analitica',
    #         'default_res_id': self.ids[0],
    #         'default_use_template': bool(template_id),
    #         'default_template_id': template_id,
    #         'default_composition_mode': 'comment',
    #         'mark_so_as_sent': True,
    #         'custom_layout': "veterinary.mail_template_data_notification_email_sale_order",
    #         'proforma': self.env.context.get('proforma', False),
    #         'force_email': True
    #     }
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'mail.compose.message',
    #         # 'views': [(compose_form_id, 'form')],
    #         # 'view_id': compose_form_id,
    #         'target': 'new',
    #         'context': ctx,
    #     }

# class MailComposeMessage(models.TransientModel):
#     _inherit = 'mail.compose.message'

#     @api.multi
#     def send_mail(self, auto_commit=False):
#         if self._context.get('default_model') == 'veterinary.analitica' and self._context.get('default_res_id') and self._context.get('mark_so_as_sent'):
#             order = self.env['veterinary.analitica'].browse([self._context['default_res_id']])
#             self = self.with_context(mail_post_autofollow=True)
#         return super(MailComposeMessage, self).send_mail(auto_commit=auto_commit)
