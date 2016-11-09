import arcpy
import os
import json
import sys
from . import restapi
from .strings import *
arcpy.env.overwriteOutput = True

try:
    THIS_DIR = os.path.dirname(__file__)
except:
    THIS_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))

JSON_TEMPLATE = os.path.join(THIS_DIR, 'bin', 'maplewood_webmap.json')
MAP_TEMPLATE = os.path.join(THIS_DIR, 'bin', 'template.mxd')
LAYER_TEMPLATE = os.path.join(THIS_DIR, 'bin', 'feature_set.lyr')
true = True
WEB_MAP_JSON = {
    "layoutOptions": {
        "titleText": "Permits"
    },
    "operationalLayers": [{
        "id": "Zoning",
        "url": "http://gis.maplewoodmn.gov/arcgis/rest/services/Projects/Zoning/MapServer",
        "title": "Maplewood Zoning",
        "visibility": true,
        "opacity": 0.5,
        "visibleLayers": [0],
    }, {
        "id": "Ramsey County",
        "url": "https://maps.co.ramsey.mn.us/arcgis/rest/services/MapRamsey/MapRamseyOperationalLayersAll/MapServer",
        "title": "Ramsey County Data",
        "visibility": true
    }, {
        "id": "Dangerous Dog",
        "url": "http://gis.bolton-menk.com/bmigis/rest/services/MPWD/Permits/FeatureServer/3",
        "visibility": true
    }, {
        "id": "Pets",
        "url": "http://gis.bolton-menk.com/bmigis/rest/services/MPWD/Permits/FeatureServer/2",
        "visibility": true
    }, {
        "id": "Chickens",
        "url": "http://gis.bolton-menk.com/bmigis/rest/services/MPWD/Permits/FeatureServer/1",
        "visibility": true
    }, {
        "id": "Kennels",
        "url": "http://gis.bolton-menk.com/bmigis/rest/services/MPWD/Permits/FeatureServer/0",
        "visibility": true
    }, ],
    "baseMap": {
        "title": "Shared Imagery Basemap",
        "baseMapLayers": [{
            "url": "http://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer",
        }, ]
    },
    "exportOptions": {
        "outputSize": [
            1500,
            1500
        ]
    },
    "mapOptions": {
        "extent": {
            "xmin": -10357891.909548426,
            "ymin": 5622353.1977390619,
            "xmax": -10356473.914621098,
            "ymax": 5623775.9693063544,
            "spatialReference": {
                "wkid": 102100,
                "latestWkid": 3857
            }
        },
    },
    "layoutOptions": {
        "copyrightText": "",
        "authorText": "",
        "legendOptions": {
            "operationalLayers": [
##                {
##                    "id": "Zoning",
##                    "subLayerIds": [0],
##                }, {
                {
                    "id": "Ramsey County",
                    "subLayerIds": [33],
                }, {
                    "id": "Dangerous Dog"
                }, {
                    "id": "Pets"
                }, {
                    "id": "Kennels"
                }, {
                    "id": "Chickens"
                },
            ]
        }
    },
    "version": "1.4",
}


def export_webmap(feature_set, out_pdf, info=' '):
    """exports a webmap

    Required:
        feature_set -- restapi.FeatureSet() object
        out_pdf -- full path to output PDF document

    Optional:
        info -- info for text box
    """
    feature_set = restapi.FeatureSet(feature_set)
##    with open(JSON_TEMPLATE, 'r') as f:
##        webmap_json = json.load(f)
    webmap_json = WEB_MAP_JSON

    mxd = arcpy.mapping.ConvertWebMapToMapDocument(webmap_json, MAP_TEMPLATE).mapDocument

    # add feature set to map
    tmp = r'in_memory\selected_parcels'
    restapi.exportFeatureSet(feature_set, tmp)

    lyr = arcpy.mapping.Layer(tmp)
    arcpy.management.ApplySymbologyFromLayer(lyr, LAYER_TEMPLATE)
    lyr.transparency = 30
    arcpy.mapping.AddLayer(mxd.activeDataFrame, lyr, 'TOP')
    layers = arcpy.mapping.ListLayers(mxd)
    lyr = [l for l in layers if l.name == os.path.basename(tmp)][0]
    lyr.name = "Selected Parcels"

    # find reference layer to move after
    ref_lyr = [l for l in layers if l.name == DANGEROUS_DOGS][0]
    arcpy.mapping.MoveLayer(mxd.activeDataFrame, ref_lyr, lyr, 'AFTER')

    # set extent for map
    ext = restapi.getFeatureExtent(feature_set)
    mxd.activeDataFrame.extent = arcpy.Describe(lyr).extent
    mxd.activeDataFrame.scale *= 1.15
    if mxd.activeDataFrame.scale < 3000:
        mxd.activeDataFrame.scale = 3000

    # set text
    elms = arcpy.mapping.ListLayoutElements(mxd)
    title_elm = [e for e in elms if e.name == 'MAP_TITLE'][0]
    info_elm = [e for e in elms if e.name == 'INFO'][0]
    info_elm.text = info
    title_elm.text = os.path.splitext(os.path.basename(out_pdf))[0].replace('_', ' ')
    legend = [e for e in elms if e.type == 'LEGEND_ELEMENT'][0]
    legend.title = ''
    legend.elementPositionX = 0.56
    legend.elementPositionY = 2.5165
    legend.elementHeight = 1.85
    legend.elementWidth = 1.85

    # export to PDF
    arcpy.mapping.ExportToPDF(mxd, out_pdf, resolution=200)
    mxd.saveACopy(os.path.join(THIS_DIR, 'bin', 'map_copy.mxd'))
    del mxd
    return out_pdf


