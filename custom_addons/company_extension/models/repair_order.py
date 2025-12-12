from odoo import models, fields, api, _
from odoo.tools import float_compare
from odoo.exceptions import UserError

class RepairOrder(models.Model):
    _inherit = 'repair.order'
    
    # Disable automatic company checking to allow cross-company lot selection
    _check_company_auto = False
    
    # Override the lot_id field to remove company restrictions
    lot_id = fields.Many2one(
        'stock.lot',
        'Lot/Serial',
        domain="[('product_id', '=', product_id)]",  # Only filter by product, not company
        check_company=False,  # Disable company consistency check
        help="Serial number of the product to repair. This field shows serial numbers from all companies."
    )
    
    # Add new state for parts approval
    state = fields.Selection(
        selection_add=[('parts_approved', 'Parts Approved')],
        ondelete={'parts_approved': 'set default'}
    )
    
    parts_approved = fields.Boolean(string="Parts Approved", default=False, tracking=True)
    parts_approved_by = fields.Many2one('res.users', string="Parts Approved By", readonly=True, tracking=True)
    parts_approved_date = fields.Datetime(string="Parts Approval Date", readonly=True, tracking=True)

    def action_validate(self):
        """Override to skip stock check for cross-company repairs"""
        self.ensure_one()
        
        if self.filtered(lambda repair: any(m.product_uom_qty < 0 for m in repair.move_ids)):
            raise UserError(_("You can not enter negative quantities."))
        
        if not self.product_id or not self.product_id.is_storable:
            return self._action_repair_confirm()
        
        # Skip stock availability check if lot belongs to different company
        if self.lot_id and self.lot_id.company_id and self.lot_id.company_id != self.company_id:
            return self._action_repair_confirm()
        
        # Otherwise, perform normal stock validation
        return super(RepairOrder, self).action_validate()
    
    def action_approve_parts(self):
        """Approve the parts selected for repair"""
        for repair in self:
            if not repair.move_ids:
                raise UserError(_("Please add parts to repair before approving."))
            repair.write({
                'parts_approved': True,
                'parts_approved_by': self.env.user.id,
                'parts_approved_date': fields.Datetime.now(),
                'state': 'parts_approved'
            })
        return True
    
    def action_repair_start(self):
        """Override to check parts approval before starting repair"""
        for repair in self:
            # If there are parts but not approved, prevent starting repair
            if repair.move_ids and not repair.parts_approved:
                raise UserError(_("Parts must be approved before starting the repair."))
        
        return super(RepairOrder, self).action_repair_start()

    def action_repair_done(self):
        """Override to handle cross-company lot repairs without stock moves"""
        # Identify cross-company repairs
        cross_company_repairs = self.filtered(
            lambda r: r.lot_id and r.lot_id.company_id and r.company_id and r.lot_id.company_id != r.company_id
        )
        
        if cross_company_repairs:
            # For cross-company repairs, skip stock move creation
            # Just mark the repair as done without moving inventory
            precision = self.env['decimal.precision'].precision_get('Product Unit')
            
            # Cancel moves with 0 quantity
            cross_company_repairs.move_ids.filtered(lambda m: m.product_uom.is_zero(m.quantity))._action_cancel()
            
            for repair in cross_company_repairs:
                # Mark all moves as picked
                if all(not move.picked for move in repair.move_ids):
                    repair.move_ids.picked = True
                
                # Update sale order line if exists
                if repair.sale_order_line_id:
                    ro_origin_product = repair.sale_order_line_id.product_template_id
                    no_service_policy = 'service_policy' not in self.env['product.template']
                    if ro_origin_product.type == 'service' and (no_service_policy or ro_origin_product.service_policy == 'ordered_prepaid'):
                        repair.sale_order_line_id.qty_delivered = repair.sale_order_line_id.product_uom_qty
                
                # Process existing moves without creating new stock move for the repaired product
                if repair.move_ids:
                    repair.move_ids._action_done(cancel_backorder=True)
                    
                    for sale_line in repair.move_ids.sale_line_id:
                        price_unit = sale_line.price_unit
                        sale_line.write({'product_uom_qty': sale_line.qty_delivered, 'price_unit': price_unit})
            
            # Mark repairs as done
            cross_company_repairs.write({'state': 'done'})
            return True
        else:
            # For same-company repairs, use standard process
            return super(RepairOrder, self).action_repair_done()
