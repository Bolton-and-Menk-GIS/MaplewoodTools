#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      calebma
#
# Created:     24/05/2016
# Copyright:   (c) calebma 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import arcpy
import sys
sys.path.append(r'\\arcserver1\GIS\MPWD\_Basemap\ESRI\Scripts\Toolbox')
from mpwd_lib import permits

if __name__ == '__main__':

    # get arguments
    args =[arcpy.GetParameter(i) for i in range(arcpy.GetArgumentCount()-2)]

    # run it
    url, out_fs = permits.kennel_permits(*args)
    arcpy.AddMessage(url)
