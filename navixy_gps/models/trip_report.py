# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
import requests
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

HEADERS = {'Accept': 'application/json'}
API_HASH = '0e7850f9427e5133ca1cccc2fd3f5104'
NAVIXY_URL = 'https://api.gaikham.com/'

class GPSTripReport(models.Model):
    _name = 'gps.trip.report'

    technic_id      = fields.Many2one('technic', 'Technic', required=True)
    nav_report_id   = fields.Integer('Navixy report ID', readonly=True)
    line_ids        = fields.One2many('gps.trip.report.line', 'report_id', 'Report lines', readonly=True)
    date_from       = fields.Datetime('Date from', required=True)
    date_to         = fields.Datetime('Date to', required=True)

    def create_report(self):
        req = {
            'hash': API_HASH,
            'trackers': [self.technic_id.gps_tracker_id],
            'from': self.date_from,
            'to': self.date_to,
            'time_filter': {"from": "00:00:00",
                           "to": "23:59:59",
                           "weekdays": [1,2,3,4,5,6,7]},
            'plugin': {
                "hide_empty_tabs": True,
                "plugin_id": 4,
                "show_seconds": False,
                "include_summary_sheet_only": False,
                "split": True,
                "show_idle_duration": True,
                "show_coordinates": False,
                "filter": True,
                "group_by_driver": False}
        }
        # _logger.info(req)
        r = requests.post(url=NAVIXY_URL+'report/tracker/generate', headers=HEADERS, json=req)
        if r.status_code == 200:
            self.nav_report_id = r.json()['id']
        else:
            raise UserError(_('Connection error!'))
        # _logger.info(r.json())
        return

    def retrieve_report(self):
        if not self.nav_report_id:
            return
        req = {
            'hash': API_HASH,
            'report_id': self.nav_report_id
        }
        r = requests.post(url=NAVIXY_URL+'report/tracker/retrieve', headers=HEADERS, json=req)
        if r.status_code == 200:
            self.line_ids.unlink()
            for day in r.json()['report']['sheets'][0]['sections'][0]['data']:
                for row in day['rows']:
                    if row['length']['raw'] > 0:
                        self.line_ids.create({
                            'report_id':    self.id,
                            'line_date':    day['header'],
                            'from_loc':     row['from']['v'],
                            'to_loc':       row['to']['v'],
                            'length':       row['length']['v'],
                            'time_sec':     row['time']['raw'],
                            'time_string':  row['time']['v'],
                            'avg_speed':    row['avg_speed']['v'],
                            'max_speed':    row['max_speed']['v'],
                            'idle_sec':     row['idle_duration']['raw'],
                            'idle_string':  row['idle_duration']['v'],
                            'fuel_consumption': row['sensor_61560']['raw']
                        })
        else:
            raise UserError(_('Connection error!'))
        return


class GPSTripReportLines(models.Model):
    _name = 'gps.trip.report.line'

    line_date   = fields.Char('Line date')
    report_id   = fields.Many2one('gps.trip.report', required=True)
    from_loc    = fields.Many2one('gps.zone','From', ondelete='restrict')
    to_loc      = fields.Many2one('gps.zone','To', ondelete='restrict')
    length      = fields.Float('Length')
    time_sec    = fields.Float('Time seconds')
    time_string = fields.Char('Time')
    avg_speed   = fields.Float('Average speed')
    max_speed   = fields.Float('Max speed')
    fuel_consumption    = fields.Float('Fuel consumption')
    idle_sec            = fields.Float('Idle duration (sec)')
    idle_string         = fields.Char('Idle duration')
