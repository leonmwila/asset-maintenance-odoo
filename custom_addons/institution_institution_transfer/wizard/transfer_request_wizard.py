from odoo import api, fields, models, _
from odoo.exceptions import UserError


class InstitutionTransferRequest(models.TransientModel):
    _name = 'institution.transfer.request.wizard'
    _description = 'Institution Transfer Request Wizard'

    dest_company_id = fields.Many2one('res.company', string='Institution', required=True)
    dest_location_id = fields.Many2one(
        'stock.location',
        string='Location',
        required=True,
        domain="[('usage', '=', 'internal'), ('company_id', 'in', [False, dest_company_id])]")

    def action_confirm(self):
        lot_ids = self.env.context.get('active_ids', [])
        if not lot_ids:
            raise UserError(_("No assets selected for transfer."))

        lots = self.env['stock.lot'].browse(lot_ids)
        transfers = []
        for lot in lots:
            quant = self.env['stock.quant'].search([
                ('lot_id', '=', lot.id),
                ('location_id.usage', '=', 'internal'),
                ('quantity', '>', 0),
            ], limit=1)
            if not quant:
                raise UserError(_("No available stock found for asset %s.") % lot.display_name)

            transfers.append({
                'lot_id': lot.id,
                'source_company_id': quant.location_id.company_id.id or lot.company_id.id,
                'source_location_id': quant.location_id.id,
                'dest_company_id': self.dest_company_id.id,
                'dest_location_id': self.dest_location_id.id,
                'state': 'pending',
            })

        self.env['institution.transfer'].create(transfers)
        return {'type': 'ir.actions.act_window_close'}
