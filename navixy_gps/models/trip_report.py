# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from magic import flatten_trip
import logging
import datetime
from gps_report import parse_datetime
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

class GPSTripReport(models.Model):
    _name = 'gps.trip.report'
    _inherit = ['gps.report']

    # technic_id      = fields.Many2one('technic', 'Technic', required=True)
    line_ids        = fields.One2many('gps.trip.report.line', 'report_id', 'Report lines', readonly=True)

    def get_plugin(self):
        return {
                "hide_empty_tabs": True,
                "plugin_id": 4,
                "show_seconds": False,
                "include_summary_sheet_only": False,
                "split": True,
                "show_idle_duration": True,
                "show_coordinates": False,
                "filter": True,
                "group_by_driver": False}

    def process_json(self, res):
        self.line_ids.unlink()
        zone_obj = self.env['gps.zone']
        trip_list = flatten_trip(res)
        for trip in trip_list:
            for technic_id in self.env['technic'].search([('gps_tracker_id','=',trip['tracker_id'])]):
                self.line_ids.create({
                    'report_id':    self.id,
                    'technic_id':   technic_id.id,
                    'line_date':    trip['line_date'],
                    'from_loc_char':trip['from'],
                    'to_loc_char'  :trip['to'],
                    'from_loc':     zone_obj.parse_text(trip['from']),
                    'to_loc':       zone_obj.parse_text(trip['to']),
                    'from_time':    parse_datetime(trip['date_char'],trip['from']),
                    'to_time':      parse_datetime(trip['date_char'],trip['to']),
                    'length':       trip['length'],
                    'time_sec':     trip['time_sec'],
                    'time_string':  trip['time_string'],
                    'avg_speed':    trip['avg_speed'],
                    'max_speed':    trip['max_speed'],
                    'idle_sec':     trip['idle_sec'],
                    'idle_string':  trip['idle_string'],
                    'fuel_consumption': trip['fuel_consumption']
                })
        return


class GPSTripReportLines(models.Model):
    _name = 'gps.trip.report.line'

    line_date   = fields.Date('Line date')
    technic_id  = fields.Many2one('technic', ondelete='restrict')
    report_id   = fields.Many2one('gps.trip.report', required=True, ondelete='cascade')
    from_loc    = fields.Many2one('gps.zone','From', ondelete='restrict')
    to_loc      = fields.Many2one('gps.zone','To', ondelete='restrict')
    from_loc_char   = fields.Char('From')
    to_loc_char     = fields.Char('To')
    from_time   = fields.Datetime('From time')
    to_time   = fields.Datetime('To time')
    length      = fields.Float('Length')
    time_sec    = fields.Float('Time seconds')
    time_string = fields.Char('Time')
    avg_speed   = fields.Float('Average speed')
    max_speed   = fields.Float('Max speed')
    fuel_consumption    = fields.Float('Fuel consumption')
    idle_sec            = fields.Float('Idle duration (sec)')
    idle_string         = fields.Char('Idle duration')

