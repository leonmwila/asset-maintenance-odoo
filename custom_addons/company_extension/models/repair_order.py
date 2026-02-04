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
        'Asset Serial',
        domain="[('product_id', '=', product_id)]",  # Base filter; refined by onchange
        check_company=False,  # Disable company consistency check
        help="Serial number of the asset to repair. This field shows serial numbers from all companies."
    )

    def _get_repair_lot_domain(self):
        """Return lot domain based on selected asset and customer."""
        domain = []
        if self.product_id:
            domain.append(('product_id', '=', self.product_id.id))
        if self.partner_id:
            domain.append(('company_id.partner_id', 'child_of', self.partner_id.id))
        return domain

    @api.onchange('partner_id', 'product_id')
    def _onchange_partner_product_lot_domain(self):
        domain = []
        for repair in self:
            domain = repair._get_repair_lot_domain()
            if repair.lot_id:
                partner_ok = not repair.partner_id or (
                    repair.lot_id.company_id and repair.lot_id.company_id.partner_id and
                    repair.lot_id.company_id.partner_id in repair.partner_id.child_ids | repair.partner_id
                )
                if repair.lot_id.product_id != repair.product_id or not partner_ok:
                    repair.lot_id = False
        return {'domain': {'lot_id': domain}}
    
    # Add new state for parts approval
    state = fields.Selection(
        selection_add=[('parts_approved', 'Parts Approved')],
        ondelete={'parts_approved': 'set default'}
    )
    
    parts_approved = fields.Boolean(string="Parts Approved", default=False, tracking=True)
    parts_approved_by = fields.Many2one('res.users', string="Parts Approved By", readonly=True, tracking=True)
    parts_approved_date = fields.Datetime(string="Parts Approval Date", readonly=True, tracking=True)
    
    # Add Operations/Services fees
    fees_lines = fields.One2many('repair.fee', 'repair_id', string='Operations')
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                   default=lambda self: self.env.company.currency_id)
    fees_amount = fields.Monetary(string='Operations Total', compute='_compute_fees_amount', store=True)
    parts_amount = fields.Monetary(string='Parts Total', compute='_compute_parts_amount', store=True)
    total_amount = fields.Monetary(string='Total', compute='_compute_total_amount', store=True)
    # Link to automatically created invoice (customer invoice)
    invoice_id = fields.Many2one('account.move', string='Invoice', copy=False, readonly=True)
    
    # Payment tracking fields
    payment_state = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
    ], string='Payment Status', default='not_paid', tracking=True)
    paid_amount = fields.Monetary(string='Paid Amount', default=0.0, tracking=True)
    balance_amount = fields.Monetary(string='Balance', compute='_compute_balance_amount', store=True)
    payment_date = fields.Date(string='Payment Date', tracking=True)
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('cheque', 'Cheque'),
        ('card', 'Card'),
    ], string='Payment Method', tracking=True)
    payment_reference = fields.Char(string='Payment Reference', tracking=True)
    received_by = fields.Many2one('res.users', string='Received By', tracking=True)
    
    @api.depends('fees_lines.price_subtotal')
    def _compute_fees_amount(self):
        for repair in self:
            repair.fees_amount = sum(repair.fees_lines.mapped('price_subtotal'))
    
    @api.depends('move_ids', 'move_ids.product_id')
    def _compute_parts_amount(self):
        """Compute total cost of parts used"""
        for repair in self:
            total = 0.0
            for move in repair.move_ids:
                # Use product cost from product
                cost = move.product_id.standard_price if move.product_id else 0.0
                total += cost * move.product_uom_qty
            repair.parts_amount = total
    
    @api.depends('fees_amount', 'parts_amount')
    def _compute_total_amount(self):
        for repair in self:
            repair.total_amount = repair.fees_amount + repair.parts_amount
    
    @api.depends('total_amount', 'paid_amount')
    def _compute_balance_amount(self):
        for repair in self:
            repair.balance_amount = repair.total_amount - repair.paid_amount
    
    @api.onchange('paid_amount', 'total_amount')
    def _onchange_paid_amount(self):
        """Auto-update payment state based on paid amount"""
        for repair in self:
            if repair.paid_amount <= 0:
                repair.payment_state = 'not_paid'
            elif repair.paid_amount >= repair.total_amount:
                repair.payment_state = 'paid'
            else:
                repair.payment_state = 'partial'
    
    def action_mark_paid(self):
        """Mark repair as fully paid"""
        for repair in self:
            repair.write({
                'paid_amount': repair.total_amount,
                'payment_state': 'paid',
                'payment_date': fields.Date.today(),
                'received_by': self.env.user.id,
            })
        return True

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

    @api.model_create_multi
    def create(self, vals_list):
        """Create repair orders and automatically generate a customer invoice for each new repair.

        The invoice is created from operations/fees lines and parts (move_ids) when present.
        """
        records = super(RepairOrder, self).create(vals_list)
        invoices = self.env['account.move']
        for rec in records:
            try:
                inv_vals = rec._prepare_invoice_vals()
                if inv_vals and inv_vals.get('invoice_line_ids'):
                    inv = self.env['account.move'].sudo().create(inv_vals)
                    # Link invoice to repair
                    rec.invoice_id = inv.id
                    invoices |= inv
            except Exception:
                # Don't block repair creation if invoicing fails; log and continue
                _logger = getattr(self, '_logger', None) or __import__('logging').getLogger('odoo.addons.company_extension')
                _logger.exception('Failed to auto-create invoice for Repair Order %s', rec.name)
        return records

    def _prepare_invoice_vals(self):
        """Prepare `account.move` values for this repair order.

        Returns dict usable with `account.move.create()`.
        """
        self.ensure_one()
        # Basic invoice header
        partner = self.partner_id or self.picking_id.partner_id
        if not partner:
            return {}
        currency = self.currency_id.id if hasattr(self, 'currency_id') and self.currency_id else (self.env.company.currency_id.id)
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_origin': self.name,
            'invoice_user_id': self.user_id.id if self.user_id else self.env.user.id,
            'company_id': self.company_id.id if self.company_id else self.env.company.id,
            'currency_id': currency,
            'invoice_line_ids': [],
        }

        # Add fee lines (operations/services)
        for fee in self.fees_lines:
            line = {
                'name': fee.name or (fee.product_id.name if fee.product_id else 'Operation'),
                'product_id': fee.product_id.id if fee.product_id else False,
                'quantity': fee.product_uom_qty or 1.0,
                'price_unit': fee.price_unit or 0.0,
                'tax_ids': [(6, 0, fee.tax_id.ids)] if fee.tax_id else False,
            }
            invoice_vals['invoice_line_ids'].append((0, 0, line))

        # Add parts lines (stock moves)
        for move in self.move_ids.filtered(lambda m: m.product_uom_qty):
            product = move.product_id
            if not product:
                continue
            # Use sale price (list price) as default unit price
            price_unit = getattr(product, 'list_price', 0.0) or 0.0
            # Taxes from product
            taxes = product.taxes_id.ids if hasattr(product, 'taxes_id') else []
            line = {
                'name': product.name,
                'product_id': product.id,
                'quantity': move.product_uom_qty,
                'price_unit': price_unit,
                'tax_ids': [(6, 0, taxes)] if taxes else False,
            }
            invoice_vals['invoice_line_ids'].append((0, 0, line))

        # If no lines to invoice, return empty dict
        if not invoice_vals['invoice_line_ids']:
            return {}
        return invoice_vals
