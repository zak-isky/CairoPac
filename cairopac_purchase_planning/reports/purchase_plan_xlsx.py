from odoo import models


class PurchasePlanXlsx(models.AbstractModel):
    _name = 'report.isky_purchase_customizations.purchase_plan_report'

    def generate_xlsx_report(self, workbook, data, plans):
        for obj in plans:
            report_name = obj.name
            # One sheet by partner
            sheet = workbook.add_worksheet(report_name[:31])
            bold = workbook.add_format({'bold': True, 'border': 1, 'align': 'center'})
            cell = workbook.add_format({'bold': False, 'border': 1, 'align': 'center'})
            row = 0
            col = 0
            sheet.merge_range(row, col, row, col + 5, obj.name, bold)
            row += 1
            col = 0

            sheet.write(row, col, 'plan Date', bold)
            col += 1
            sheet.write(row, col, obj.plan_date and str(obj.plan_date) or '', cell)
            col += 1
            sheet.write(row, col, 'Date from', bold)
            col += 1
            sheet.write(row, col, obj.date_from and str(obj.date_from) or '', cell)
            col += 1
            sheet.write(row, col, 'Date from', bold)
            col += 1
            sheet.write(row, col, obj.date_to and str(obj.date_to) or '', cell)
            # write headers
            row += 2
            col = 0
            sheet.write(row, col, 'product', bold)
            col += 1
            sheet.write(row, col, 'Quantity on hand', bold)
            col += 1
            sheet.write(row, col, 'Quantity', bold)
            col += 1
            sheet.write(row, col, 'Purchased Quantity', bold)
            col += 1
            row += 1

            for line in obj.purchase_plan_line_ids:
                col = 0
                sheet.write(row, col, line.product_id.display_name, cell)
                col += 1
                sheet.write(row, col, line.qty_available, cell)
                col += 1
                sheet.write(row, col, line.product_qty, cell)
                col += 1
                sheet.write(row, col, line.done_qty, cell)
                col += 1
                row += 1
