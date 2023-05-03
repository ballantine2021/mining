# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
import datetime
from gps_report import parse_datetime
from magic import flatten_stops
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class GPSStopReport(models.Model):
    _name = 'gps.stop.report'
    _inherit = ['gps.report']

    line_ids = fields.One2many('gps.stop.report.line', 'report_id', 'Report lines', readonly=True)

    def get_plugin(self):
        return {
                "hide_empty_tabs": True,
                "plugin_id": 6,
                "show_seconds": False,
                "show_coordinates": False,
                "filter": False,}

    def process_json(self, res):
        self.line_ids.unlink()
        zone_obj = self.env['gps.zone']
        token = self.env['gps.report'].get_config('magic_token')
        stop_report = flatten_stops(res, token)
        for stop in stop_report:
            for technic_id in self.env['technic'].search([('gps_tracker_id','=',stop['tracker_id'])]):
                line_date = datetime.datetime.strptime(stop['date'], "%Y-%m-%d").date()
                zone = zone_obj.parse_text(stop['location'])
                self.line_ids.create({
                    'report_id':    self.id,
                    'technic_id':   technic_id.id,
                    'product_id': self.env['gps.zone'].search([('id', '=', zone)]).product_id.id,
                    'technic_model_id':   technic_id.technic_model_id.id,
                    'ownership_type':   technic_id.ownership_type,
                    'line_date':    line_date,
                    'loc' :         zone_obj.parse_text(stop['location']),
                    'from_time':    parse_datetime(stop['date'],stop['start']),
                    'to_time':      parse_datetime(stop['date'],stop['end']),
                    'idle_sec':     stop['idle_sec'],
                    'idle_string':  stop['idle_string'],
                    'ignition_sec':     stop['ignition_sec'],
                    'ignition_string':  stop['ignition_string'],
                    'idle_hour':     float(stop['idle_sec'])/3600 if stop['idle_sec'] is not None and float(stop['idle_sec']) != 0 else 0,
                    'ignition_hour':  float(stop['ignition_sec'])/3600 if stop['ignition_sec'] is not None and float(stop['ignition_sec']) != 0 else 0,
                })
        return

class GPSStopReportLines(models.Model):
    _name = 'gps.stop.report.line'

    line_date   = fields.Date('Line date')
    technic_id  = fields.Many2one('technic', ondelete='restrict')
    product_id = fields.Many2one('product.template','Zone type', ondelete='restrict')
    technic_model_id  = fields.Many2one('technic.model', ondelete='restrict')
    ownership_type = fields.Selection([('own', 'Own'),
                                    ('leasing', 'Leasing'),
                                    ('partner', 'Partner'),
                                    ('rental', 'Rental')], 'Ownership type')
    report_id   = fields.Many2one('gps.stop.report', required=True, ondelete='cascade')
    loc         = fields.Many2one('gps.zone','Zone', ondelete='restrict')
    loc_char    = fields.Char('Zone')
    from_time   = fields.Datetime('From time')
    to_time     = fields.Datetime('To time')
    idle_sec        = fields.Float('Idle second')
    idle_hour        = fields.Float('Idle hour')
    idle_string        = fields.Char('Idle')
    ignition_sec    = fields.Float('Ignition seconds')
    ignition_string    = fields.Char('Ignition string')
    ignition_hour    = fields.Float('Ignition hour')
