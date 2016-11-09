import arcpy
import sys
import os
import arial10
import datetime
from xlwt import Workbook, Borders, Font, XFStyle
import bmi

arcpy.env.qualifiedFieldNames = False
arcpy.env.overwriteOutput = True

def CreateExcelSpreadsheet(table, output_excel, where='', use_alias=True):
    """Exports table to excel

    Required:
        table -- input table
        output_excel -- output excel table (.xlsx, .xls)

    Optional:
        where -- where clause for output excel file
        use_alias -- use field alias name for column headers. Default is True
    """
    if not output_excel.endswith('.xls'):
        output_excel = os.path.splitext(output_excel)[0] + '.xls'

    # build field dict
    fieldNames = [(f.name, f.aliasName) for f in arcpy.ListFields(table) if f.type != 'Geometry']
    fields = [f[1] if use_alias else f[0] for f in fieldNames]
    widths = {i: arial10.fitwidth(f) + 1024 for i,f in enumerate(fields)}

    # get field values  *Changed from type dict to list
    with arcpy.da.SearchCursor(table, [f[0] for f in fieldNames], where_clause=where) as rows:
        values = [r for r in rows]

    # Create spreadsheet
    wb = Workbook()
    ws = wb.add_sheet('Sheet 1')
    cols = len(fields)
    rows = len(values) + 1

    # set styles
    #***************************************************************************
    borders = Borders()
    borders.left = Borders.THIN
    borders.right = Borders.THIN
    borders.top = Borders.THIN
    borders.bottom = Borders.THIN

    style = XFStyle()
    style.borders = borders

    # headers
    fntHeaders = Font()
    fntHeaders.bold = True
    fntHeaders.height = 220

    styleHeaders = XFStyle()
    styleHeaders.font = fntHeaders
    styleHeaders.borders = borders

    # for date fields
    styleDate = XFStyle()
    styleDate.borders = borders
    styleDate.num_format_str = 'MM/DD/YYYY'
    #***************************************************************************

    # write headers and freeze panes
    for ci,field in enumerate(fields):
        ws.write(0, ci, field, styleHeaders)

    # freeze headers
    ws.set_panes_frozen(True)
    ws.set_horz_split_pos(1)

    # fill in values
    start = 1
    for vals in values:
        for i, value in enumerate(vals):
            isDate = isinstance(value, datetime.datetime)
            v_width = arial10.fitwidth(unicode(value).strip())
            if value is None:
                value = ''
            ws.write(start, i, unicode(value) if not isDate else value, styleDate if isDate else style)
            if v_width > widths[i]:
                widths[i] = v_width
        start += 1

        if not start % 1000:
            ws.flush_row_data()

    # autofit column widths
    for ci,width in widths.iteritems():
        ws.col(ci).width = int(width + 256) # just a little more padding

    # save workbook
    wb.save(output_excel)
    del wb
    bmi.Message('Created: %s' %os.path.abspath(output_excel))
    return output_excel

if __name__ == '__main__':

    # run tool
    bmi.passArgs(CreateExcelSpreadsheet)
