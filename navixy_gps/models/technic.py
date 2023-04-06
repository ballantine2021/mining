# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Technic(models.Model):
    _inherit = 'technic'

    gps_tracker_id = fields.Integer('GPS tracker ID')