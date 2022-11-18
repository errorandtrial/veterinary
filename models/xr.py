# -*- coding: utf-8 -*-

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang



class Xr(models.Model):
    _name = 'veterinary.xr'
    _inherit = ['mail.thread']    
    _order = "date desc"
    name = fields.Char(string='Test ID', required=True, copy=False, readonly=True,index=True, default=lambda self: _('New'))
    animal = fields.Many2one('veterinary.animal')
    partner_id = fields.Many2one('res.partner', string='Owner', required=True)
    appointment_id = fields.Many2one('veterinary.appointment',string='Appointment',required=True)  
    date = fields.Datetime(string='Date', related='appointment_id.dateOfAppointment')
    user_id = fields.Many2one('res.users', string='Doctor')
    xr_projection = fields.Char('Projection')
    findings_xr = fields.Char('Findings')    
    image = fields.Binary(
        "Image", attachment=True,
        help="This field holds the image used as image for the product, limited to 1024x1024px.")
    other_xr = fields.Text('Other')
    overall_assessment_xr = fields.Text('Overall Assessment')
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('increment_xr') or _('New')
        res = super(Xr, self).create(vals)
        return res  

    @api.multi
    def action_xr_sent(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('veterinary', 'email_template_radiology')[1]
        except ValueError:
            template_id = False
        # try:
        #     compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        #     print 'tempalte mail'
        # except ValueError:
        #     compose_form_id = False
        ctx = {
            'default_model': 'veterinary.xr',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "veterinary.email_template_radiology",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            # 'views': [(compose_form_id, 'form')],
            # 'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
