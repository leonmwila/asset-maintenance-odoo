from odoo import api, fields, models, _
from odoo.exceptions import UserError


class InstitutionTransfer(models.Model):
    _name = 'institution.transfer'
    _description = 'Institution Asset Transfer'
    _order = 'create_date desc'

    lot_id = fields.Many2one('stock.lot', string='Asset', required=True, ondelete='cascade')
    product_id = fields.Many2one(related='lot_id.product_id', string='Product', store=True, readonly=True)
    source_company_id = fields.Many2one('res.company', string='Source Institution', readonly=True)
    source_location_id = fields.Many2one('stock.location', string='Source Location', readonly=True)
    dest_company_id = fields.Many2one('res.company', string='Destination Institution', required=True)
    dest_location_id = fields.Many2one('stock.location', string='Destination Location', required=True)
    state = fields.Selection(
        [('pending', 'Pending Approval'), ('approved', 'Approved'), ('cancelled', 'Cancelled')],
        default='pending',
        string='Status',
        tracking=True,
    )
    requested_by = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user, readonly=True)
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True)
    approved_date = fields.Datetime(string='Approved On', readonly=True)

    def action_approve(self):
        for transfer in self.filtered(lambda t: t.state == 'pending'):
            transfer._perform_transfer()
            transfer.write({
                'state': 'approved',
                'approved_by': self.env.user.id,
                'approved_date': fields.Datetime.now(),
            })
        return True

    def action_cancel(self):
        self.filtered(lambda t: t.state == 'pending').write({'state': 'cancelled'})
        return True

    def _perform_transfer(self):
        self.ensure_one()
        lot = self.lot_id
        quant = self._get_lot_quant(lot)
        if not quant:
            raise UserError(_("No available stock found for asset %s.") % lot.display_name)

        source_location = quant.location_id
        dest_location = self.dest_location_id
        if source_location == dest_location:
            raise UserError(_("Source and destination locations are the same for %s.") % lot.display_name)

        quantity = quant.quantity
        if quantity <= 0:
            raise UserError(_("No available quantity to transfer for %s.") % lot.display_name)

        quant_model = self.env['stock.quant']
        quant_model._update_available_quantity(lot.product_id, source_location, -quantity, lot_id=lot)
        quant_model._update_available_quantity(lot.product_id, dest_location, quantity, lot_id=lot)

        lot.company_id = self.dest_company_id.id
        self.source_company_id = source_location.company_id.id or self.dest_company_id.id
        self.source_location_id = source_location.id

    def _get_lot_quant(self, lot):
        return self.env['stock.quant'].search([
            ('lot_id', '=', lot.id),
            ('location_id.usage', '=', 'internal'),
            ('quantity', '>', 0),
        ], limit=1)

    def _get_internal_picking_type(self, company):
        if not company:
            return self.env['stock.picking.type'].search([('code', '=', 'internal')], limit=1)
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'internal'),
            ('warehouse_id.company_id', '=', company.id),
        ], limit=1)
        if picking_type:
            return picking_type
        return self.env['stock.picking.type'].search([('code', '=', 'internal')], limit=1)
