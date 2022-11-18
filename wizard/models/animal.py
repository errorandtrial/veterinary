# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from ast import literal_eval

class Animal(models.Model):
    _name = 'veterinary.animal'
    image = fields.Binary(
        "Image", attachment=True,
        help="This field holds the image used as image for the product, limited to 1024x1024px.")
    name = fields.Char('Animal Name', required=True)
    microchip_number = fields.Char('Microchip Number',required=True)
    age = fields.Integer('Age', required=True)
    appointment_id = fields.Many2many('veterinary.appointment')
    total_appointment = fields.Char('Total',compute='_total_appointment')
    colour =fields.Selection (
        (('b','B'),('c','C'), ('g','G') ,('other','Other'))
        ,required=True)
    sex =fields.Selection ((
        ('f','F'),('m','M'), ('g','G'))
        ,required=True)
    bread =fields.Selection ((
        ('tb','TB'),('ar','AR'),
        ('wb','WB'),('p','P'),('other','Other'))
        ,required=True,string="Breed & Use")
    partner_id = fields.Many2one('res.partner',string='Owner', required=True)
    evaluation = fields.One2many('veterinary.evaluation','animal',readonly=True)
    # bloodtest = fields.One2many('veterinary.bloodtest','animal',readonly=True)
    # citology = fields.One2many('veterinary.citology','animal',readonly=True)
    # echography = fields.One2many('veterinary.echography','animal',readonly=True)
    # xr = fields.One2many('veterinary.xr','animal',readonly=True)

    _sql_constraints = [
    ('microchio_uniq', 'unique(microchip_number)', 'Microchip already exists!')
    ]

    @api.multi
    def _total_appointment(self):
        self.total_appointment = len(self.appointment_id)

    def appointment_view(self):
        action = self.env.ref('veterinary.action_appointment_form')
        result = action.read()[0]
        result['domain'] = [('animals', '=', self.id)]
        return result

class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Partner'
    animal_picking_id = fields.One2many('veterinary.animal','partner_id', string="Animal Id")

    def open_animal(self):
        action = self.env.ref('veterinary.action_animal_form')
        result = action.read()[0]
        result['domain'] = [('partner_id', '=', self.id)]
        return result
