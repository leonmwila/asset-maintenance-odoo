from odoo import models, fields, api


class StockLot(models.Model):
    _inherit = 'stock.lot'

    print_barcode = fields.Boolean(
        string='Print Barcode',
        help='Check this to include this serial number in barcode printing'
    )

    def action_open_label_layout(self):
        """Open the label layout wizard for printing serial number barcodes"""
        view_id = self.env.ref('product.product_label_layout_form_view').id
        return {
            'name': 'Choose Labels Layout',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'product.label.layout',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'context': {
                'default_product_ids': [],
                'default_lot_ids': self.ids,
                'default_print_format': '4x7',
            }
        }
