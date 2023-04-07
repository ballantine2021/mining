# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
import requests, re
from odoo.exceptions import UserError
from gps_report import HEADERS, API_HASH, NAVIXY_URL
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
                if not rec:
                    self.create({
                        'name': zone['label'],
                        'navixy_id': zone['id']
                    })
        else:
            raise UserError(_('Connection error!'))
        # _logger.info(r.json())
        return

    def parse_text(self, txt):
        zone = re.search(r'\[(.*?)\]', txt)
        if zone:
            parsed = zone.group(1)
        else:
            text_split = txt.split('-')
            if len(text_split)>1:
                parsed = text_split[1]
            else:
                parsed = text_split
        for rec in self.search([('name','=',parsed)]):
            return rec.id
        return self.create({'name': parsed}).id