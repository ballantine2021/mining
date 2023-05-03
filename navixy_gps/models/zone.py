# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
import requests, re
from odoo.exceptions import UserError
from gps_report import HEADERS
_logger = logging.getLogger(__name__)

class GPSZone(models.Model):
    _name = 'gps.zone'

    name = fields.Char('Zone')
    navixy_id = fields.Integer('Navixy ID')
    product_id = fields.Many2one('product.template','Zone type')

    def _pull_data(self):
        gps_obj = self.env['gps.report']
        req = {
            'hash': gps_obj.get_config('navixy_hash'),
        }
        r = requests.post(url=gps_obj.get_config('navixy_url') + 'zone/list', headers=HEADERS, json=req)
        if r.status_code == 200:
            for zone in r.json()['list']:
                rec = self.search([('navixy_id','=',zone['id'])])
                if not rec:
                    self.create({
                        'name': zone['label'],
                        'navixy_id': zone['id']
                    })
        else:
            raise UserError(_('Connection error!'))
        return

    def parse_text(self, txt):
        zone = re.search(r'\[(.*?)\]', txt)
        if zone:
            parsed = zone.group(1)
        else:
            parsed = txt.split('-')[-1]
        for rec in self.search([('name','in',[parsed])]):
            return rec.id
        return self.create({'name': parsed}).id