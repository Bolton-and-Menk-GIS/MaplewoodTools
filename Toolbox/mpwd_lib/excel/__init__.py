#-------------------------------------------------------------------------------
# Name:        Excel
# Purpose:     Thin Excel Wrapper classes
#
# Author:      Caleb Mackey
#
# Created:     1/30/2016
#-------------------------------------------------------------------------------
import sys
import os
import datetime
import generic_styles
from xlwt import Workbook, Borders, Font, XFStyle, Formula

# default style name
DEFAULT_STYLE = 'DEFAULT_STYLE'

class ExcelWorkbook(object):
    def __init__(self, encoding='ascii', style_compression=0):
        self.wb = Workbook(encoding, style_compression)
        self.sheets = []

    def sheet(self, sheet_name=''):
        """get a sheet by name, if no name creates a new sheet"""
        if not self.sheets:
            return self.add_sheet(sheet_name)

        else:
            for sheet in self.sheets:
                if sheet.name == sheet_name:
                    return sheet

    def add_sheet(self, sheet_name='Sheet 1', headers=[], header_line_no=0, use_borders=False, styleHeaders=None, styleDict={}, widths={}):
        ws = self.wb.add_sheet(sheet_name, cell_overwrite_ok=True)
        self.sheets.append(ExcelSheet(ws, headers, header_line_no, use_borders, styleHeaders, styleDict, widths))
        return self.sheets[-1]

    def save(self, filename):
        """saves excel file"""
        if os.path.splitext(filename)[-1] not in ('.xls', '.xlsx'):
            filename = os.path.splitext(filename)[0] + '.xls'

        for sheet in iter(self):
            sheet.autoFit()

        self.wb.save(filename)
        return filename

    def __iter__(self):
        """generator to iterate through sheets"""
        for sheet in self.sheets:
            yield sheet

class ExcelSheet(object):
    """thin wrapper class for easy generation of exce tables"""
    def __init__(self, ws, headers, header_line_no=0, use_borders=False, styleHeaders=None, styleDict={}, widths={}):
        self.headers = headers
        self.header_line_no = header_line_no
        self._currentRowIndex = self.header_line_no + 1
        self.ws = ws
        self.rows = []
        self.borders = None
        self._defaultStyle = XFStyle()

        # columnn widths
        if isinstance(widths, dict) and len(widths):
            self._explicit_widths = True
            self.__colwidths = widths
        else:
            self._explicit_widths = False
            self.__colwidths = {i:len(h) for i,h in enumerate(self.headers)}

        #***************************************************************************
        if use_borders is True:
            self.borders = generic_styles.defaultBorders

        self.normStyle = generic_styles.defaultStyle

        # headers
        if not isinstance(styleHeaders, XFStyle):
            self.styleHeaders = generic_styles.defaultStyleHeaders
            if use_borders is True:
                self.styleHeaders.borders = self.borders

        else:
            self.styleHeaders = styleHeaders

        # for date fields if no styleDict
        self.styleDate = generic_styles.styleDate
        #***************************************************************************
        #
        # instance styles defined by user or defaults
        if all(map(lambda s: isinstance(s, XFStyle), styleDict.values())):
            self.styleDict = styleDict
            if DEFAULT_STYLE in styleDict:
                self._defaultStyle = self.styleDict[DEFAULT_STYLE]
        else:
            self.styleDict = {}
            self._defaultStyle = self.normStyle
            print 'set to normal style...'

        self.writeHeaders()

    def writeHeaders(self):
        """writes the headers"""
        # write headers and freeze panes
        for ci,field in enumerate(self.headers):
            self.ws.write(self.header_line_no, ci, field, self.styleHeaders)

        # freeze headers
        self.ws.set_panes_frozen(True)
        self.ws.set_horz_split_pos(self.header_line_no + 1)

    def setHeaders(self, headers):
        """resets headers

        headers -- list of header names
        """
        self.headers = headers
        if not self._explicit_widths:
            self.__colwidths = {i:len(h) for i,h in enumerate(self.headers)}
        self.writeHeaders()

    def addRow(self, *args, **kwargs):
        """add a row to the sheet

        Optional:
            args -- values for fields in their order
            kwargs -- values for fields by name. There are also 2 special kwargs
                supported for setting styles to the row to override the instance
                styleDict.  They are listed below:

                style -- overriding style to be applied to ENTIRE row (must be XFStyle)
                styleDict -- overriding styleDict that sets styles by field names, values
                    must be instances of XFStyle.
        """
        default = [None] * len(self.headers)
        # by index (*args)
        for i,arg in enumerate(args):
            default[i] = arg

        # by name (*kwargs)
        cellStyle = None
        overwriteSytleDict = {}
        for name, value in kwargs.iteritems():
            if name in self.headers:
                default[self.headers.index(name)] = value

            # override this instances style dict and apply style to entire row
            elif name == 'style' and isinstance(value, XFStyle):
                cellStyle = value

            # there's an overridding styleDict
            elif name == 'styleDict' and isinstance(value, dict) and all(map(lambda v: isinstance(v, XFStyle), value.values())):
                overwriteSytleDict = value

        # write it out
        for i, value in enumerate(default):

            # set appropriate style, defaults are used if no styleDict applied,
            #  style can be overwritten if "style" or "styleDict" is explicitly passed in kwargs
            if cellStyle:
                style = cellStyle

            elif self.headers[i] in overwriteSytleDict:
                style = overwriteSytleDict[self.headers[i]]

            # no force overwridding of styles, use this instances' set style
            elif self.headers[i] in self.styleDict:
                style = self.styleDict[self.headers[i]]

            else:
                # No style preferences, format to date if necessary
                if isinstance(value, datetime.datetime):
                    style = self.styleDate

                # default, no style preference whatsoever
                else:
                    style = self._defaultStyle

            if value is None:
                value = ''

            # update dict to autofit columns
            if len(unicode(value)) > self.__colwidths[i] and not self._explicit_widths:
                self.__colwidths[i] = len(unicode(value))

            # write value
            if isinstance(value, basestring):
                value = unicode(value)
            self.ws.write(self._currentRowIndex, i, value, style=style)

        self._currentRowIndex += 1
        self.rows.append(default)

        # flush every 1000 records
        if not self._currentRowIndex % 1000 and hasattr(self.ws, 'flush_rows'):
            self.ws.flush_rows()

    def autoFit(self, widths=None):
        if widths is None:
            widths = self.__colwidths
        for i, width in sorted(widths.iteritems()):
            self.ws.col(i).width = min([width * 350, 65535])

    def __len__(self):
        """gets count of records (don't count the headers)"""
        return self._currentRowIndex - 1

    def __iter__(self):
        """iterate through rows"""
        for row in self.rows:
            yield row
