#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      calebma
#
# Created:     15/04/2016
# Copyright:   (c) calebma 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from xlwt import Alignment, XFStyle, Borders, Font

# **************************************************************************************
# generic styles
#
# default borders
defaultBorders = Borders()
defaultBorders.bottom = Borders.THIN
defaultBorders.top = Borders.THIN
defaultBorders.right = Borders.THIN
defaultBorders.left = Borders.THIN

# center align
alignCenter = Alignment()
alignCenter.horz = Alignment.HORZ_CENTER
alignCenter.vert = Alignment.VERT_CENTER

# Top alignment, should be used for all cells
alignTop = Alignment()
alignTop.vert = Alignment.VERT_TOP

# header centered and wrapped
alignWrap = Alignment()
alignWrap.horz = Alignment.HORZ_CENTER
alignWrap.wrap = Alignment.WRAP_AT_RIGHT

# generic font, 11 point Calibri
defaultFont = Font()
defaultFont.height = 220
defaultFont.name = 'Arial'

# default heades font
headerFont = Font()
headerFont.height = 220
headerFont.name = 'Arial'
headerFont.bold = True

# header styles
defaultStyleHeaders = XFStyle()
defaultStyleHeaders.font = headerFont
defaultStyleHeaders.alignment.wrap = True
defaultStyleHeaders.alignment = alignCenter
defaultStyleHeaders.font = headerFont

# wrapped headers with boarder
styleHeadersWithBorder = XFStyle()
styleHeadersWithBorder.font = headerFont
styleHeadersWithBorder.alignment.wrap = True
styleHeadersWithBorder.alignment = alignWrap
styleHeadersWithBorder.borders = defaultBorders

# left alignment
alignLeft = Alignment()
alignLeft.horz = Alignment.HORZ_LEFT
alignLeft.vert = Alignment.VERT_TOP
alignLeft.wrap = Alignment.WRAP_AT_RIGHT

# right alignment
alignRight = Alignment()
alignRight.horz = Alignment.HORZ_RIGHT
alignRight.vert = Alignment.VERT_TOP
alignRight.wrap = Alignment.WRAP_AT_RIGHT

# style for left justified and wrapped
styleHeadersLeft = XFStyle()
styleHeadersLeft.font = headerFont
styleHeadersLeft.alignment.wrap = True
styleHeadersLeft.alignment = alignLeft

# style for right justified and wrapped
styleHeadersRight = XFStyle()
styleHeadersRight.font = defaultFont
styleHeadersRight.alignment.wrap = True
styleHeadersRight.alignment = alignRight

# blank line
underline = XFStyle()
uBorders = Borders()
uBorders.bottom = Borders.THIN
underline.borders = uBorders

# date format
styleDate = XFStyle()
styleDate.num_format_str = 'MM/DD/YYYY'
styleDate.font = defaultFont
styleDate.alignment = alignLeft

# currency format
styleCurrency = XFStyle()
styleCurrency.num_format_str = '#,##0.00'
styleCurrency.font = defaultFont
styleCurrency.alignment = alignRight

# style for section-township-range
zfillStyle = XFStyle()
zfillStyle.num_format_str = '00'
zfillStyle.font = defaultFont
zfillStyle.alignment = alignLeft

# default
defaultStyle = XFStyle()
defaultStyle.font = defaultFont
defaultStyle.alignment = alignLeft
