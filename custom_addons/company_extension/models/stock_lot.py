from odoo import models, fields, api

class StockLot(models.Model):
    _inherit = 'stock.lot'

    grz_number = fields.Char(string='GRZ Number', required=True)
    program_id = fields.Many2one('oe.program', string='Program', domain="[('company_id', '=', company_id)]")
    project_id = fields.Many2one('oe.project', string='Project', domain="[('company_id', '=', company_id)]")
    assigned_to = fields.Many2one(
        'hr.employee',
        string='Assigned To',
        domain="[('company_id', '=', company_id)]",
        help="Employee to whom this serial number/equipment is assigned"
    )

    @api.onchange('company_id', 'program_id', 'project_id', 'product_id')
    def _onchange_build_grz_number(self):
        for record in self:
            if not record.company_id:
                record.grz_number = ''
                continue

            company = record.company_id
            prefix = ''

            # Step 1: Determine prefix based on company_type
            if company.company_type == 'grz':
                prefix = f"GRZ/{company.company_code}/"
            else:
                prefix = f"{company.company_code}/"

            # Step 2: Append program/project/product codes
            middle = ''
            if record.program_id:
                middle += f"{record.program_id.prog_code}/"
                if record.project_id:
                    middle += f"{record.project_id.proj_code}/"
            else:
                # If no program, append product code directly
                if record.product_id:
                    middle += f"{record.product_id.categ_id.category_code or 'NO-CODE'}/"

            # If program but no project, append product code
            if record.program_id and not record.project_id and record.product_id:
                middle += f"{record.product_id.categ_id.category_code or 'NO-CODE'}/"

            # Combine so far
            record.grz_number = prefix + middle
