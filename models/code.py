# -*- coding: utf-8 -*-

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang



class Code(models.Model):
    _name = 'veterinary.code'
    name = fields.Char(string='Name')
    code = fields.Char(string='code')
    category = fields.Char(string='Category', domain="{'Diagnostic', 'Procedure', 'Drug treatment', 'Other'}" )
#    evaluations = fields.Many2many('veterinary.evaluation', 'cod_eval_rel',  'name', 'name')
    
    

    
#     @api.multi
#     def action_citologia_sent(self):
#         '''
#         This function opens a window to compose an email, with the edi sale template message loaded by default
#         '''
#         self.ensure_one()
#         ir_model_data = self.env['ir.model.data']
#         try:
#             template_id = ir_model_data.get_object_reference('veterinary', 'email_template_edi_sale')[1]
#         except ValueError:
#             template_id = False
#         # try:
#         #     compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
#         #     print 'tempalte mail'
#         # except ValueError:
#         #     compose_form_id = False
#         ctx = {
#             'default_model': 'veterinary.citologia',
#             'default_res_id': self.ids[0],
#             'default_use_template': bool(template_id),
#             'default_template_id': template_id,
#             'default_composition_mode': 'comment',
#             'mark_so_as_sent': True,
#             'custom_layout': "veterinary.mail_template_data_notification_email_sale_order",
#             'proforma': self.env.context.get('proforma', False),
#             'force_email': True
#         }
#         return {
#             'type': 'ir.actions.act_window',
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'mail.compose.message',
#             # 'views': [(compose_form_id, 'form')],
#             # 'view_id': compose_form_id,
#             'target': 'new',
#             'context': ctx,
#         }

# class MailComposeMessage(models.TransientModel):
#     _inherit = 'mail.compose.message'

#     @api.multi
#     def send_mail(self, auto_commit=False):
#         if self._context.get('default_model') == 'veterinary.citologia' and self._context.get('default_res_id') and self._context.get('mark_so_as_sent'):
#             order = self.env['veterinary.citologia'].browse([self._context['default_res_id']])
#             self = self.with_context(mail_post_autofollow=True)
#         return super(MailComposeMessage, self).send_mail(auto_commit=auto_commit)
