# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
import requests
from odoo.exceptions import UserError
from trip_report import HEADERS, API_HASH, NAVIXY_URL
_logger = logging.getLogger(__name__)

class GPSZone(models.Model):
    _name = 'gps.zone'

    name = fields.Char('Zone')
    navixy_id = fields.Integer('Navixy ID')

    def _pull_data(self):
        req = {
            'hash': API_HASH,
        }
        r = requests.post(url=NAVIXY_URL + 'zone/list', headers=HEADERS, json=req)
        if r.status_code == 200:
            for zone in r.json()['list']:
                rec = self.search([('navixy_id','=',zone['id'])])
                if rec:
                    if rec.name != zone['label']:
                        rec.name = zone['label']
                else:
                    self.create({
                        'name': zone['label'],
                        'navixy_id': zone['id']
                    })
        else:
            raise UserError(_('Connection error!'))
        # _logger.info(r.json())
        return
