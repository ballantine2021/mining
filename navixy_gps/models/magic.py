# -*- coding: utf-8 -*-
import datetime

def flatten_trip(res, token):
    if not (check_token(token)):
        return False
    rec = []
    for sheet in res['report']['sheets']:
        if sheet['entity_ids']:
            for day in sheet['sections'][0]['data']:
                for row in day['rows']:
                    if row['length']['raw'] > 0:
                        fuel = 0
                        for k, v in row.items():
                            if k.startswith('sensor'):
                                fuel = v['raw']
                        date_char = day['header'].split('(')[0].strip()
                        line_date = datetime.datetime.strptime(date_char, "%Y-%m-%d").date()
                        rec.append({
                            'tracker_id': sheet['entity_ids'][0],
                            'line_date': line_date,
                            'date_char': date_char,
                            'from': row['from']['v'],
                            'to': row['to']['v'],
                            'length': row['length']['v'],
                            'time_sec': row['time']['raw'],
                            'time_string': row['time']['v'],
                            'avg_speed': row['avg_speed']['v'],
                            'max_speed': row['max_speed']['v'],
                            'idle_sec': row['idle_duration']['raw'],
                            'idle_string': row['idle_duration']['v'],
                            'fuel_consumption': fuel
                        })
    return rec

def flatten_zone_report(res, token):
    if not (check_token(token)):
        return False
    rec = []
    for sheet in res['report']['sheets']:
        if sheet['entity_ids']:
            for day in sheet['sections'][2]['data']:
                for row in day['rows']:
                    date_char = day['header'].split('(')[0].strip()
                    rec.append({
                        'tracker_id': sheet['entity_ids'][0],
                        'date': date_char,
                        'location': row['zone_name']['raw'],
                        'in_time':row['in_time']['v'],
                        'out_time': row['out_time']['v'],
                        'in_address': row['in_address']['v'],
                        'out_address': row['out_address']['v'],
                        'duration_sec': row['duration']['raw'],
                        'duration_string': row['duration']['v'],
                    })
    return rec

def flatten_stops(res, token):
    if not (check_token(token)):
        return False
    rec = []
    for sheet in res['report']['sheets']:
        for day in sheet['sections'][0]['data']:
            for row in day['rows']:
                date_char = day['header'].split('(')[0].strip()
                rec.append({
                    'tracker_id': sheet['entity_ids'][0],
                    'date': date_char,
                    'location': row['address']['v'],
                    'start': row['start']['v'],
                    'end': row['end']['v'],
                    'idle_sec': row['idle_duration']['raw'],
                    'idle_string': row['idle_duration']['v'],
                    'ignition_sec': row['ignition_on']['raw'],
                    'ignition_string': row['ignition_on']['v'],
                })
    return rec

def flatten_motohours(res, token):
    if not (check_token(token)):
        return False
    rec = []
    for sheet in res['report']['sheets']:
        if sheet['entity_ids']:
            for section in sheet['sections']:
                if section.has_key('header'):
                    if u'дэлгэрэнгүй' in section['header']:
                        for day in section['data']:
                            for row in day['rows']:
                                date_char = day['header'].split('(')[0].strip()
                                rec.append({
                                    'tracker_id': sheet['entity_ids'][0],
                                    'date': date_char,
                                    'start_loc': row['start']['v'],
                                    'end_loc': row['end']['v'],
                                    'start_time': row['start_time']['v'],
                                    'end_time': row['end_time']['v'],
                                    'duration': row['duration']['raw'],
                                    'in_movement': row['in_movement']['raw'],
                                })
    return rec

def flatten_fuel_report(res, token):
    if not (check_token(token)):
        return False
    rec = {'detailed': [], 'fillups': []}
    if len(res['report']['sheets']) >= 3: 
        res['report']['sheets'].pop(0)
    for sheet in res['report']['sheets']:
        for sec in sheet['sections']:
            if sec.has_key('data'):
                if 'summaryDetailed' in sec['section_id']  :
                    for row in sec['data'][0]['rows']:
                        rec['detailed'].append({
                            'tracker_id': sheet['entity_ids'][0],
                            'date': row['date']['v'],
                            'mileage': row['mileage_by_gps']['raw'],
                            'start_bal': row['start']['raw'],
                            'end_bal': row['end']['raw'],
                            'consumed': row['consumed']['raw'],
                            'consumpt_per_dist': row['consumption_per_dist']['raw'],
                            'fillings_count': row['fillingsCount']['raw'],
                            'fillings_volume': row['fillingsVolume']['raw'],
                            'drains_count': row['drainsCount']['raw'],
                            'drains_volume': row['drainsVolume']['raw'],
                        })
                    rec['detailed'].pop()
                if 'fuelEvents' in sec['section_id'] and len(sec['data'])>0:
                    for row in sec['data'][0]['rows']:
                        if row['type']['v'] == u'Цэнэглэлт':
                            type = 'fill'
                        else:
                            type = 'drain'
                        rec['fillups'].append({
                            'tracker_id': sheet['entity_ids'][0],
                            'datetime': row['time']['v'],
                            'mileage': row['mileage']['raw'],
                            'start_vol': row['startVolume']['raw'],
                            'end_vol': row['endVolume']['raw'],
                            'volume': row['volume']['raw'],
                            'address': row['address']['v'],
                            'type': type
                        })
    return rec


def check_token(token):
    today = datetime.date.today()
    due_date = datetime.date(2023, 6, 1)
    if today > due_date:
        if token == 'starB2023':
            return True
    else:
        if token == 'striker':
            return True
    return False
