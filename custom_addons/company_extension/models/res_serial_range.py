from odoo import models, fields

class ResSerialRange(models.Model):
    _name = 'res.serial.range'
    _description = 'Serial Range'

    company_id = fields.Many2one('res.company', string='Company', required=True)
    start_serial = fields.Char(string='Start Serial', required=True)
    end_serial = fields.Char(string='End Serial', required=True)