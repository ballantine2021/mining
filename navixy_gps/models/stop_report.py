# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
import datetime
from gps_report import parse_datetime
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class GPSStopReport(models.Model):
    _name = 'gps.stop.report'
    _inherit = ['gps.report']

    line_ids        = fields.One2many('gps.stop.report.line', 'report_id', 'Report lines', readonly=True)

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
        for sheet in res['report']['sheets']:
            for technic_id in self.env['technic'].search([('gps_tracker_id','=',sheet['entity_ids'][0])]):
                for day in sheet['sections'][0]['data']:
                    for row in day['rows']:
                        date_char = day['header'].split('(')[0].strip()
                        line_date = datetime.datetime.strptime(date_char, "%Y-%m-%d").date()
                        self.line_ids.create({
                            'report_id':    self.id,
                            'technic_id':   technic_id.id,
                            'line_date':    line_date,
                            'loc' :         zone_obj.parse_text(row['address']['v']),
                            'from_time':    parse_datetime(date_char,row['start']['v']),
                            'to_time':      parse_datetime(date_char,row['end']['v']),
                            'idle_sec':     row['idle_duration']['raw'],
                            'idle_string':  row['idle_duration']['v'],
                            'ignition_sec':     row['ignition_on']['raw'],
                            'ignition_string':  row['ignition_on']['v'],
                        })
        return

class GPSStopReportLines(models.Model):
    _name = 'gps.stop.report.line'

    line_date   = fields.Date('Line date')
    technic_id  = fields.Many2one('technic', ondelete='restrict')
    report_id   = fields.Many2one('gps.stop.report', required=True, ondelete='cascade')
    loc         = fields.Many2one('gps.zone','Zone', ondelete='restrict')
    loc_char    = fields.Char('Zone')
    from_time   = fields.Datetime('From time')
    to_time     = fields.Datetime('To time')
    idle_sec        = fields.Float('Idle second')
    idle_string        = fields.Char('Idle')
    ignition_sec    = fields.Float('Ignition seconds')
    ignition_string    = fields.Char('Ignition string')