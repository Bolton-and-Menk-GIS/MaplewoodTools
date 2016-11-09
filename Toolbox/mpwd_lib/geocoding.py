import os
import arcpy
import json
from collections import namedtuple
import restapi
#from . import restapi
from . import requests
from .strings import *

ramsey_gc = restapi.Geocoder(RAMSEY_GC)

def geocode_address(address, outSR=RAMSEY_WKID):
    """geocodes an address, tries Ramsey County geocoder first, if no good results then try google"""
    gcr = ramsey_gc.findAddressCandidates(address, outSR=outSR)
    if gcr:
        pt = gcr[0].location
        return arcpy.PointGeometry(arcpy.Point(pt['x'], pt['y']), arcpy.SpatialReference(outSR))

    else:
        # try google
        if not 'maplewood' in address.lower():
            address += ' maplewood, mn 55109'

        r = googleGC(address)
        loc = r.location
        if loc['x'] is not None:
            pt_wgs = arcpy.PointGeometry(arcpy.Point(loc['x'], loc['y']), arcpy.SpatialReference(4326))
            return pt_wgs.projectAs(arcpy.SpatialReference(outSR))

    return None

def reverse_geocode(fs):
    """reverse geocodes and address

    Required:
        fs -- input point geometry as feature set
    """
##    g = restapi.Geometry(json.loads(fs.JSON))
    g = restapi.Geometry(fs)

    address = ''

    # do reverse geocode
    try:
        result = ramsey_gc.reverseGeocode(g.JSON, outSR=RAMSEY_WKID).result
        address = result.attributes['Street']
    except:
        result = None

    if result is None:
        # try google's reverse geocode
        point_geom = g.asShape()
        if g.spatialReference != 4326:
            point_geom = point_geom.projectAs(arcpy.SpatialReference(4326))

        result = googleRG(point_geom.centroid.X, point_geom.centroid.Y)
        address = result.address

    return (address if address is not None else '' + ' MAPLEWOOD MN 55119').upper().strip()

def googleGC(address):
    """ Google API Geocoder

    address -- address required in this format: "100 E Main St, Mankato, MN 56001"
    """
    r = requests.get(GOOGLE + 'address={}&sensor=true'.format(address)).json()
    return googleResponse(r)

def googleRG(lat, lon):
    """ Google API reverse Geocode (mimics restapi.GeocodeResult object)

    lat -- y coordinate
    lon -- x coordinate
    """
    params = "latlng={lat},{lon}&sensor=true".format(lat=lat,lon=lon)
    r = requests.get(GOOGLE + params).json()
    return googleResponse(r)

def googleResponse(r):
    """handler for google maps API geocode JSON response"""
    goog = namedtuple('GeocodeResult_Google', 'address attributes location score')
    if r['results']:
        gapi = r['results'][0]
        atts = gapi['address_components']
        try:
            city = [d['long_name'] for d in iter(atts) if 'locality' in d['types']][0]
        except: city = 'N/A'
        try:
            _zip = [d['long_name'] for d in iter(atts) if 'postal_code' in d['types']][0]
        except: _zip = 'N/A'
        try:
            state = [d['short_name'] for d in iter(atts) if 'administrative_area_level_1' in d['types']][0]
        except: state = 'N/A'
        formatted_response = {'address': gapi['formatted_address'].split(',')[0].upper(),
                              'attributes': {'City': city.upper(),
                                             'State': state,
                                             'Zip': _zip},
                              'location': {'x': gapi['geometry']['location']['lng'],
                                           'y': gapi['geometry']['location']['lat']},
                              'score': None}


        return goog(**formatted_response)
    else:
        return goog(**{'address': None,
             'attributes': {'City': None,
                            'State': None,
                            'Zip': None},
             'location': {'x': None,
                          'y': None},
             'score': None})

if __name__ == '__main__':

    null = None
    fs = {"displayFieldName":"","fieldAliases":{"OBJECTID":"OBJECTID","Source":"Source"},"geometryType":"esriGeometryPoint","spatialReference":{"wkid":102100,"latestWkid":3857},"fields":[{"name":"OBJECTID","type":"esriFieldTypeOID","alias":"OBJECTID"},{"name":"Source","type":"esriFieldTypeString","alias":"Source","length":4}],"features":[{"attributes":{"OBJECTID":1,"Source":null},"geometry":{"x":-10363697.878799999,"y":5615645.7650000006}},{"attributes":{"OBJECTID":2,"Source":null},"geometry":{"x":-10362528.1516,"y":5617183.5503999963}}]}
    t = reverse_geocode(fs)
