from odoo import api, fields, models, _
from odoo import tools
from datetime import datetime, timedelta


class fuel_report_analyze(models.Model):
    _name = 'fuel.report.analyze'
    _description = 'Fuel report analyze'
    _auto = False

    line_date   = fields.Date('Line date')
    technic_id  = fields.Many2one('technic', ondelete='restrict')
    mileage     = fields.Float('Km')
    consumed    = fields.Float('Consumed')
    per_km    = fields.Float('Comsumed per km')
    per_hour    = fields.Float('Consumed per hour')
    time_hour    = fields.Float('Time hour')
    fillings_volume     = fields.Float('Fillings volume')
    technic_model_id  = fields.Many2one('technic.model', ondelete='restrict')
    ownership_type = fields.Selection([('own', 'Own'),
                                    ('leasing', 'Leasing'),
                                    ('partner', 'Partner'),
                                    ('rental', 'Rental')], 'Ownership type')   

    _order = 'line_date desc'

    def init(self):
        tools.sql.drop_view_if_exists(self.env.cr, 'fuel_report_analyze')
        self.env.cr.execute("""
            CREATE or REPLACE view fuel_report_analyze as
            SELECT trl.id , trl.technic_id, trl.technic_model_id, t.ownership_type,
            trl.line_date, trl.consumed, trl.fillings_volume, trl.mileage,
            a.time_hour ,
            (case when (trl.mileage = 0 or trl.mileage is null) then 0 else nullif(trl.consumed/trl.mileage,0) end) as per_km,
            (case when (a.time_hour = 0 or a.time_hour is null) then 0 else nullif(trl.consumed/a.time_hour,0) end) as per_hour
            FROM gps_fuel_report_line trl
            LEFT JOIN technic t ON t.id = trl.technic_id
            LEFT JOIN
            (select line_date, technic_id, sum(time_hour) as time_hour
            from gps_trip_report_line
            group by line_date, technic_id) a
            ON concat(a.line_date, a.technic_id) = concat(trl.line_date, trl.technic_id)
        """)
