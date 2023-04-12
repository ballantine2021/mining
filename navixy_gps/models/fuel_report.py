# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
import datetime
from gps_report import parse_datetime
from magic import flatten_fuel_report
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class GPSFuelReport(models.Model):
    _name = 'gps.fuel.report'
    _inherit = ['gps.report']

    detailed_line_ids = fields.One2many('gps.fuel.report.line', 'report_id', 'Detailed lines', readonly=True)
    fill_line_ids = fields.One2many('gps.fuel.fill.report', 'report_id', 'Fill/drain lines', readonly=True)

    def get_plugin(self):
        return  {
            "show_seconds":False,
            "plugin_id":10,
            "graph_type":"mileage",
            "detailed_by_dates":True,
            "include_summary_sheet_only":False,
            "use_ignition_data_for_consumption":False,
            "include_mileage_plot":False,
            "filter":True,
            "include_speed_plot":False,
            "smoothing":False,
            "surge_filter":True,
            "surge_filter_threshold":0.2,
            "speed_filter":False,
            "speed_filter_threshold":10
        }

    def process_json(self, res):
        zone_obj = self.env['gps.zone']
        token = self.env['gps.report'].get_config('magic_token')
        report = flatten_fuel_report(res, token)
        for row in report['detailed']:
            for technic_id in self.env['technic'].search([('gps_tracker_id', '=', row['tracker_id'])]):
                self.detailed_line_ids.create({
                    'report_id':    self.id,
                    'technic_id':   technic_id.id,
                    'line_date':    datetime.datetime.strptime(row['date'], "%Y-%m-%d").date(),
                    'mileage':      row['mileage'],
                    'start_bal':    row['start_bal'],
                    'end_bal':      row['end_bal'],
                    'consumed':     row['consumed'],
                    'consumpt_per_dist':    row['consumpt_per_dist'],
                    'fillings_count':       row['fillings_count'],
                    'fillings_volume':      row['fillings_volume'],
                    'drains_count':         row['drains_count'],
                    'drains_volume':        row['drains_volume'],
                })

        for row in report['fillups']:
            for technic_id in self.env['technic'].search([('gps_tracker_id', '=', row['tracker_id'])]):
                zone_id = zone_obj.parse_text(row['address'])
                if zone_id:
                    self.fill_line_ids.create({
                        'report_id': self.id,
                        'technic_id': technic_id.id,
                        'line_datetime': datetime.datetime.strptime(row['datetime'], "%Y-%m-%d %H:%M"),
                        'mileage': row['mileage'],
                        'start_vol': row['start_vol'],
                        'end_vol': row['end_vol'],
                        'volume': row['volume'],
                        'location_id': zone_id,
                        'type': row['type']
                    })
        return


class GPSFuelReportLines(models.Model):
    _name = 'gps.fuel.report.line'

    line_date   = fields.Date('Line date')
    technic_id  = fields.Many2one('technic', ondelete='restrict')
    report_id   = fields.Many2one('gps.fuel.report', required=True, ondelete='cascade')
    mileage     = fields.Float('Mileage')
    start_bal   = fields.Float('Start balance')
    end_bal     = fields.Float('End balance')
    consumed    = fields.Float('Consumed')
    consumpt_per_dist   = fields.Float('Consumption per distance')
    fillings_count      = fields.Integer('Filling count')
    fillings_volume     = fields.Float('Fillings volume')
    drains_count        = fields.Integer('Drains count')
    drains_volume       = fields.Float('Drains volume')

class GPSFuelFillReport(models.Model):
    _name = 'gps.fuel.fill.report'

    line_datetime = fields.Datetime('Line date')
    technic_id  = fields.Many2one('technic', ondelete='restrict')
    report_id   = fields.Many2one('gps.fuel.report', required=True, ondelete='cascade')
    volume      = fields.Float('Volume')
    start_vol   = fields.Float('Start volume')
    end_vol     = fields.Float('End volume')
    type        = fields.Selection([('fill','Fill'),('drain','Drain')], 'Fill/drain')
    mileage     = fields.Float('Mileage')
    location_id = fields.Many2one('gps.zone', 'Location', ondelete='restrict')