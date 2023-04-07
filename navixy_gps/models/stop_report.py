# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
import requests, re, pytz
import datetime
from gps_report import HEADERS, API_HASH, NAVIXY_URL, parse_datetime
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

NAVIXY_TZ = pytz.timezone('Asia/Ulaanbaatar')

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

    def retrieve(self):
        req = {
            'hash': API_HASH,
            'report_id': self.nav_report_id
        }
        r = requests.post(url=NAVIXY_URL+'report/tracker/retrieve', headers=HEADERS, json=req)
        if r.status_code == 200:
            self.line_ids.unlink()
            zone_obj = self.env['gps.zone']
            for sheet in r.json()['report']['sheets']:
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
            self.state = 'done'
        else:
            _logger.info(r.content)
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