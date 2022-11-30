# -*- coding: utf-8 -*-

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang


class Evaluation(models.Model):
    _name = 'veterinary.evaluation'
    _inherit = ['mail.thread']

    @api.multi
    def default_stage(self):
        return self.env['veterinary.evaluation.stages'].search([('name', '=', 'New')])

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['veterinary.evaluation.stages'].search([])
        return stage_ids

    name = fields.Char('Name', compute='_compute_name')
    animal = fields.Many2one('veterinary.animal', string='Animal', readonly=True)
    appointment_id = fields.Many2one('veterinary.appointment', string='Appointment')
    description = fields.Char(string="Reason for consultation", store=True, related='appointment_id.description')

    current_illness = fields.Text('Current illness')
    stage_id = fields.Many2one('veterinary.evaluation.stages', string='Stage', required=True, default=default_stage,
                               group_expand='_read_group_stage_ids')
    user_id = fields.Many2one('res.users', string='Doctor', index=True, track_visibility='onchange',
                              default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string='Owner', required=True, readonly=True)
    conditions = fields.Many2many('veterinary.code', 'cod_eval_rel', 'name', 'code',
                                  domain="[('category', '=', 'Condition')]")
    procedures = fields.Many2many('veterinary.code', 'proc_eval_rel', 'name', 'code',
                                  domain="[('category', '=', 'Procedure')]")
    prescriptions = fields.Many2many('product.product', 'prod_eval_rel', 'name', 'product_id')

    # Musculoskeletal System Page
    conformation = fields.Char('Conformation')
    feet_shoeing = fields.Char('Feet and Shoeing')
    le = fields.Char('LF')
    rf = fields.Char('RF')
    lh = fields.Char('LH')
    rh = fields.Char('RH')
    neck_back_pelvis = fields.Char('Neck Back Pelvis')
    flexion_tests = fields.Char('Flexion Tests')
    ridden = fields.Char('Ridden')
    diagnostic_imaging = fields.Char('Diagnostic Imaging')
    walk = fields.Char('Walk')
    trot = fields.Char('Trot')

    # Respiratory System
    res_general = fields.Char('General')
    lung_auscultation = fields.Char('Lung auscultation')
    upper_airway_endoscopy = fields.Char('Upper airway endoscopy')

    # Cardiovascular System
    cardi_general = fields.Char('General')
    auscultation = fields.Char('Auscultation')
    ecg = fields.Char('ECG')

    # Gastrointestinal System
    gest_general = fields.Char('General')
    worming_history = fields.Char('Worming Histroy')
    teeth = fields.Char('Teeth')

    # Nervous System
    nevr_general = fields.Char('General')
    mentation = fields.Char('Mentation')
    gait = fields.Char('Gait')
    eyes = fields.Char('Eyes')

    # Reproductive and Uniary System
    fig = fields.Char('Female / Intact Male / Gelding')
    testicles = fields.Char('Testicles')
    vulva = fields.Char('Vulva')

    # Skin
    scars = fields.Char('Scars - Traumatic / Surgical')
    melanomas = fields.Char('Tumours - Melanomas Sarcoids')
    Dermatitis = fields.Char('Dermatitis')
    Allergy = fields.Char('Allergy')
    skin_other = fields.Char('Other')

    other = fields.Text('Other')
    overall_assessment = fields.Text('Overall Assessment')
    recommendations = fields.Text('Recommendations')

    def _compute_name(self):
        self.name = self.appointment_id.name
        return True

    @api.one
    def action_create_invoice(self):
        self.appointment_id.action_create_invoice

    @api.one
    def action_done(self):
        self.appointment_id.action_done

    @api.multi
    def action_evaluation_sent(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('veterinary', 'email_template_edi_sale')[1]
        except ValueError:
            template_id = False
        ctx = {
            'default_model': 'veterinary.evaluation',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "veterinary.email_template_edi_sale",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': ctx,
        }


class EvaluationStages(models.Model):
    _name = 'veterinary.evaluation.stages'
    name = fields.Char('Stage')
