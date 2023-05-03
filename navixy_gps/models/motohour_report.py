# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
import datetime
from gps_report import parse_datetime
from magic import flatten_motohours
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class GPSMotohourReport(models.Model):
    _name = 'gps.motohour.report'
    _inherit = ['gps.report']

    line_ids = fields.One2many('gps.motohour.report.line', 'report_id', 'Report lines', readonly=True)

    def get_plugin(self):
        return  {
            "hide_empty_tabs":True,
            "plugin_id":7,
            "show_seconds":True,
            "show_detailed":True,
            "include_summary_sheet_only":False,
            "filter":True
        }

    def process_json(self, res):
        self.line_ids.unlink()
        zone_obj = self.env['gps.zone']
        token = self.env['gps.report'].get_config('magic_token')
        motohour_report = flatten_motohours(res, token)
        for motohour in motohour_report:
            for technic_id in self.env['technic'].search([('gps_tracker_id','=',motohour['tracker_id'])]):
                line_date = datetime.datetime.strptime(motohour['date'], "%Y-%m-%d").date()
                self.line_ids.create({
                    'report_id':    self.id,
                    'technic_id':   technic_id.id,
                    # 'product_id': self.env['gps.zone'].search([('id', '=', zone)]).product_id.id,
                    'technic_model_id': technic_id.technic_model_id.id,
                    'ownership_type':   technic_id.ownership_type,
                    'line_date':        line_date,
                    'start_loc' :       zone_obj.parse_text(motohour['start_loc']),
                    'end_loc' :         zone_obj.parse_text(motohour['end_loc']),
                    'start_time':    parse_datetime(motohour['date'],motohour['start_time']),
                    'end_time':      parse_datetime(motohour['date'],motohour['end_time']),
                    'in_movement_sec':     motohour['in_movement'],
                    'duration_sec':     motohour['duration'],
                    'in_movement_hour':     float(motohour['in_movement'])/3600 if motohour['in_movement'] is not None and float(motohour['in_movement']) != 0 else 0,
                    'duration_hour':  float(motohour['duration'])/3600 if motohour['duration'] is not None and float(motohour['duration']) != 0 else 0,
                })
        return

class GPSMotohourReportLines(models.Model):
    _name = 'gps.motohour.report.line'

    line_date   = fields.Date('Line date')
    technic_id  = fields.Many2one('technic', 'Technic', ondelete='restrict')
    technic_model_id  = fields.Many2one('technic.model', 'Technic model', ondelete='restrict')
    ownership_type = fields.Selection([('own', 'Own'),
                                    ('leasing', 'Leasing'),
                                    ('partner', 'Partner'),
                                    ('rental', 'Rental')], 'Ownership type')
    report_id   = fields.Many2one('gps.motohour.report', required=True, ondelete='cascade')
    start_loc   = fields.Many2one('gps.zone','Start location', ondelete='restrict')
    end_loc     = fields.Many2one('gps.zone','End location', ondelete='restrict')
    start_time   = fields.Datetime('Start time')
    end_time     = fields.Datetime('End time')
    in_movement_sec = fields.Float('In movement seconds')
    in_movement_hour = fields.Float('In movement hours')
    duration_sec    = fields.Float('Duration seconds')
    duration_hour   = fields.Float('Duration hour')
