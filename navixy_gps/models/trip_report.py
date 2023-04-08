# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
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
        for sheet in res['report']['sheets']:
            for technic_id in self.env['technic'].search([('gps_tracker_id','=',sheet['entity_ids'][0])]):
                for day in sheet['sections'][0]['data']:
                    for row in day['rows']:
                        if row['length']['raw'] > 0:
                            date_char = day['header'].split('(')[0].strip()
                            line_date = datetime.datetime.strptime(date_char, "%Y-%m-%d").date()
                            self.line_ids.create({
                                'report_id':    self.id,
                                'technic_id':   technic_id.id,
                                'line_date':    line_date,
                                'from_loc_char' : row['from']['v'],
                                'to_loc_char'   :row['to']['v'],
                                'from_loc':     zone_obj.parse_text(row['from']['v']),
                                'to_loc':       zone_obj.parse_text(row['to']['v']),
                                'from_time':    parse_datetime(date_char,row['from']['v']),
                                'to_time':      parse_datetime(date_char,row['to']['v']),
                                'length':       row['length']['v'],
                                'time_sec':     row['time']['raw'],
                                'time_string':  row['time']['v'],
                                'avg_speed':    row['avg_speed']['v'],
                                'max_speed':    row['max_speed']['v'],
                                'idle_sec':     row['idle_duration']['raw'],
                                'idle_string':  row['idle_duration']['v'],
                                'fuel_consumption': row['sensor_61560']['raw']
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

