# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import requests, datetime, re, pytz
import logging
_logger = logging.getLogger(__name__)

GPS_MODELS = ['gps.trip.report','gps.stop.report','gps.zone.report','gps.fuel.report']
HEADERS = {'Accept': 'application/json'}
NAVIXY_TZ = pytz.timezone('Asia/Ulaanbaatar')

class GPSReport(models.AbstractModel):
    _name = 'gps.report'

    nav_report_id   = fields.Integer('Navixy report ID', readonly=True)
    date            = fields.Date('Date', required=True)
    state           = fields.Selection([('in_process','In process'),('done','Done'),('fail','Fail')])

    def generate_reports(self):
        for report_model in GPS_MODELS:
            self.create_report(report_model)


    def create_report(self, report_model):
        report_obj = self.env[report_model]
        # Get the current date
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        # Get the start time for yesterday
        start_time = datetime.datetime.combine(yesterday, datetime.time.min)
        # Get the end time for yesterday
        end_time = datetime.datetime.combine(yesterday, datetime.time.max)
        technic_ids = self.env['technic'].search([('gps_tracker_id','!=',False)])

        req = {
            'hash': self.get_config('navixy_hash'),
            'trackers': [t.gps_tracker_id for t in technic_ids],
            'from': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'to': end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'time_filter': {"from": "00:00:00",
                           "to": "23:59:59",
                           "weekdays": [1,2,3,4,5,6,7]},
            'plugin': report_obj.get_plugin()
        }
        r = requests.post(url=self.get_config('navixy_url')+'report/tracker/generate', headers=HEADERS, json=req)
        if r.status_code == 200:
            json = r.json()
            if json['success']:
                report_obj.create({
                    'nav_report_id': r.json()['id'],
                    'date': yesterday,
                    'state': 'in_process',
                })
        return

    def check_report(self):
        for report_model in GPS_MODELS:
            for report in self.env[report_model].search([('state','=','in_process')]):
                req = {
                    'hash': self.get_config('navixy_hash'),
                    'report_id': report.nav_report_id
                }
                r = requests.post(url=self.get_config('navixy_url')+'report/tracker/status', headers=HEADERS, json=req)
                if r.status_code == 200:
                    json = r.json()
                    if json['success'] and json['percent_ready'] == 100:
                        self.retrieve_report(report)

    def retrieve_report(self, report):
        req = {
            'hash': self.get_config('navixy_hash'),
            'report_id': report.nav_report_id
        }
        r = requests.post(url=self.get_config('navixy_url')+'report/tracker/retrieve', headers=HEADERS, json=req)
        if r.status_code == 200:
            report.process_json(r.json())
            report.state = 'done'
        else:
            _logger.info(r.content)
            report.state = 'fail'

    def get_config(self, parameter):
        config = self.env['ir.config_parameter'].search([('key','=',parameter)])
        if config:
            return config[0].value
        else:
            _logger.error('Navixy %s not found!' % parameter)
            return False



def parse_datetime(char_date, char_hour_min):
    server_tz = pytz.timezone('GMT')
    parsed = re.search(r'\d{2}:\d{2}', char_hour_min).group()  # extract time using regex
    from_dt = datetime.datetime.strptime(char_date + ' ' + parsed, '%Y-%m-%d %H:%M')
    return NAVIXY_TZ.localize(from_dt, is_dst=None).astimezone(server_tz)