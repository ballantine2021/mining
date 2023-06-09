# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
import datetime
from magic import flatten_zone_report
from gps_report import parse_datetime
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class GPSZoneReport(models.Model):
    _name = 'gps.zone.report'
    _inherit = ['gps.report']

    line_ids        = fields.One2many('gps.zone.report.line', 'report_id', 'Report lines', readonly=True)

    def get_plugin(self):
        minutes = self.env['gps.report'].get_config('config_min_minutes_in_zone')
        return  {
            "hide_empty_tabs":True,
            "plugin_id":8,
            "show_seconds":False,
            "show_mileage":False,
            "show_not_visited_zones":False,
            "min_minutes_in_zone":minutes,
            "hide_charts":True,
            "zone_ids":[z.navixy_id for z in self.env['gps.zone'].search([('navixy_id','!=',False)])]}

    def process_json(self, res):
        self.line_ids.unlink()
        zone_obj = self.env['gps.zone']
        token = self.env['gps.report'].get_config('magic_token')
        stop_list = flatten_zone_report(res, token)
        for stop in stop_list:
            for technic_id in self.env['technic'].search([('gps_tracker_id','=',stop['tracker_id'])]):
                line_date = datetime.datetime.strptime(stop['date'], "%Y-%m-%d").date()
                for zone_id in zone_obj.search([('navixy_id','=',stop['location'])]):
                    self.line_ids.create({
                        'report_id':    self.id,
                        'technic_id':   technic_id.id,
                        'line_date':    line_date,
                        'location_id':  zone_id.id,
                        'in_datetime':  parse_datetime(stop['date'],stop['in_time']),
                        'out_datetime': parse_datetime(stop['date'],stop['out_time']),
                        'in_loc':      self.get_zone_id(stop['in_address']),
                        'out_loc':      self.get_zone_id(stop['out_address']),
                        'duration_sec': stop['duration_sec'],
                        'duration_string': stop['duration_string'],
                        'duration_hour':     float(stop['duration_sec'])/3600 if stop['duration_sec'] is not None and float(stop['duration_sec']) != 0 else 0,
                        'product_id': zone_id.product_id.id,
                        'technic_model_id':   technic_id.technic_model_id.id,
                        'ownership_type':   technic_id.ownership_type,                        
                    })
        return

    def get_zone_id(self, address):
        zone_obj = self.env['gps.zone']
        zone_id = zone_obj.search([('name','in',[address])])
        if zone_id:
            return zone_id.id
        else:
            return zone_id.create({'name': address}).id

class GPSZoneReportLines(models.Model):
    _name = 'gps.zone.report.line'

    line_date   = fields.Date('Line date')
    technic_id  = fields.Many2one('technic', ondelete='restrict')
    report_id   = fields.Many2one('gps.zone.report', required=True, ondelete='cascade')
    location_id = fields.Many2one('gps.zone', 'Location', ondelete='restrict')
    in_loc      = fields.Many2one('gps.zone','In location', ondelete='restrict')
    out_loc     = fields.Many2one('gps.zone','Out location', ondelete='restrict')
    in_datetime    = fields.Datetime('In time')
    out_datetime   = fields.Datetime('Out time')
    duration_sec        = fields.Float('Duration /sec/')
    duration_string     = fields.Char('Duration')
    duration_hour        = fields.Float('Duration hour')
    product_id = fields.Many2one('product.template','Zone type', ondelete='restrict')
    technic_model_id  = fields.Many2one('technic.model', ondelete='restrict')
    ownership_type = fields.Selection([('own', 'Own'),
                                    ('leasing', 'Leasing'),
                                    ('partner', 'Partner'),
                                    ('rental', 'Rental')], 'Ownership type')