#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      calebma
#
# Created:     23/05/2016
# Copyright:   (c) calebma 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import geocoding
import os
import arcpy
import time
import shutil
import json
import textwrap
from . import restapi
from . import excel
from .strings import *
from . import mailing
from .utils import *
from . import export

OID = 'esriFieldTypeOID'
SHAPE = 'esriFieldTypeGeometry'

@timeit
def chicken_permits(point=None, address=None, name='', permits='', num_chickens=0, status='Approved', date_issued=None, date_expired=None):
    """

    """
    NOW = datetime.datetime.now()
    NEXT_YEAR = NOW + datetime.timedelta(days=365)
    if point in (None, '', '#') and address:
        # we will geocode the address
        pt = geocoding.geocode_address(address)
        pt_geom = restapi.Geometry(pt)

    else:
        pt_geom = restapi.Geometry(point)
        pt = pt_geom.asShape()

    # query the zoning and parcels
    if not address:
        # reverse geocode
        address = geocoding.reverse_geocode(pt_geom.json)
    address = address.upper()

    # check zoning and parcels
    zone_ms = restapi.MapService(ZONING)
    zone_lyr = zone_ms.layer(ZONE_LAYER)

    d = {'geometryType': pt_geom.geometryType,
         'returnGeometry': 'true',
         'geometry': pt_geom.json,
         'inSR' : pt_geom.spatialReference,
         'outSR': RAMSEY_WKID}

    cursor = zone_lyr.cursor(fields=['cityzoning'], records=1, add_params=d)

    isRes = False
    if cursor:
        for row in cursor:
            isRes = row[0] == 'r1'

    if isRes:
        # now query parcels
        pars_ms = restapi.MapService(RAMSEY_MS)
        pars_lyr = pars_ms.layer(PARCEL_LAYER)

        cursor = pars_lyr.cursor(add_params=d, records=1)
        if cursor:
            # grab the first polygon
            try:
                par_poly = cursor.getRow(0).geometry
            except IndexError:
                raise RuntimeError('Could not find any parcels that intersect the point!')

            # select all parcels that intersect the geometry
            par_d = {'geometryType': par_poly.geometryType,
                     'returnGeometry': 'true',
                     'geometry': par_poly,
                     'inSR' : par_poly.spatialReference,
                     'outSR': RAMSEY_WKID}

            # add to feature service
            fs = restapi.FeatureService(PERMITS_FS)
            chickens = fs.layer(CHICKENS)

            # write excel file and get mailing labels
            stamp = time.strftime('%Y%m%d%H%M%S')
            out_dir = os.path.join(TEMP_FILES, 'Chicken_Permits_{}'.format(stamp))
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)

            # clean up???
            if CLEANUP_TEMP_FILES is True and os.path.basename(TEMP_FILES) == 'TempFiles':
                remove_files(TEMP_FILES)

            # get field filter for spreadsheet only
            fields = [f.name for f in pars_lyr.fields
                      if 'shape' not in f.name.lower()
                      and 'objectid' not in f.name.lower()
                      and f.type not in (OID, SHAPE)]
            cursor = pars_lyr.cursor(add_params=par_d)

            addresses = []

            wb = excel.ExcelWorkbook()
            ws = wb.add_sheet(headers=fields)
            feats = []

             # form json
            for permit in permits.split(','):
                feats.append({'geometry': pt_geom.json,
                             'attributes': {'Owner_Name': name,
                                            'Primary_Address': address,
                                            'License': permit,
                                            'Num_Chickens': num_chickens,
                                            'Status': status,
                                            'Date_Issued': restapi.date_to_mil(date_issued or NOW),
                                            'Date_Expired': restapi.date_to_mil(date_expired or NEXT_YEAR)
                    }})

            add_res = chickens.addFeatures(feats)

            # add rows to excel and extract addresses
            for feature in cursor.features:
                ft = feature['attributes']
                valrow = [ft[f] for f in fields]
                ws.addRow(*valrow)
                addr_list = [ft[f] for f in (TAX_NAME, TAX_ADDR, TAX_CSZ)]
                addresses.append(addr_list)

            # generate mailing labels
            pdf = os.path.join(out_dir, 'MailingLabels_avery5160.pdf')
            xls = os.path.join(out_dir, 'Chicken_Permit_Parcels.xls')
            wb.save(xls)
            mailing.avery5160(pdf, addresses)

            # export webmap
            if 'MAPLEWOOD' in address:
                a_split = address.split('MAPLEWOOD')
                address = '\r\n'.join([a_split[0], 'MAPLEWOOD' + a_split[1]])
            permit_string = '\r\n\t '.join(textwrap.wrap('Permits: ' + ', '.join(permits.split(',')), 35))
            info = '\r\n'.join(['\r\n'.join(textwrap.wrap(name, 35)), address, '\r\n', permit_string])
            out_pdf = os.path.join(out_dir, 'Chicken_Permits.pdf')
            export.export_webmap(cursor.json, out_pdf, info)

            # zip folder and delete original
            zipped = zipdir(out_dir)

            #********************************************************************************************************************************
            # DELETE ME FOR MAPLEWOOD
            try:
                shutil.copy(zipped, os.path.join(r'\\arcserver3\wwwroot\TempFiles', os.path.basename(zipped)))
            except:
                pass
            #*********************************************************************************************************************************
            url = '/'.join([TEMP_FILES_URL, os.path.basename(zipped)])
            try:
                shutil.rmtree(out_dir)
            except:
                pass

            arcpy.SetParameter(8, '<a href="{}" target="_blank">Download Zip File</a>'.format(url))
            arcpy.SetParameter(9, arcpy.AsShape(json.dumps(cursor.json), True))
            return url, cursor.json

    else:
        raise RuntimeError('The point is not within a residential zoning area!')


@timeit
def kennel_permits(point=None, address=None, name='', kennel_license='', permits='', status='Approved', date_issued=None, date_expired=None):
    """

    """
    NOW = datetime.datetime.now()
    NEXT_YEAR = NOW + datetime.timedelta(days=365)
    if point in (None, '', '#') and address:
        # we will geocode the address
        pt = geocoding.geocode_address(address)
        pt_geom = restapi.Geometry(pt)

    else:
        pt_geom = restapi.Geometry(point)
        pt = pt_geom.asShape()

    # query the zoning and parcels
    if not address:
        # reverse geocode
        address = geocoding.reverse_geocode(pt_geom.json)
    address = address.upper()

    d = {'geometryType': pt_geom.geometryType,
         'returnGeometry': 'true',
         'geometry': pt_geom.json,
         'inSR' : pt_geom.spatialReference,
         'outSR': RAMSEY_WKID}

    # now query parcels
    pars_ms = restapi.MapService(RAMSEY_MS)
    pars_lyr = pars_ms.layer(PARCEL_LAYER)

    cursor = pars_lyr.cursor(add_params=d, records=1)
    if cursor:
        # grab the first polygon
        try:
            par_poly = cursor.getRow(0).geometry
        except IndexError:
            raise RuntimeError('Could not find any parcels that intersect the point!')

        # select all parcels that intersect the geometry
        par_d = {'geometryType': par_poly.geometryType,
                 'returnGeometry': 'true',
                 'geometry': par_poly.json,
                 'distance': 150,
                 'units': 'esriSRUnit_Foot',
                 'inSR' : par_poly.spatialReference,
                 'outSR': RAMSEY_WKID}

        # add to feature service
        fs = restapi.FeatureService(PERMITS_FS)
        kennels = fs.layer(KENNELS)
        pets = fs.layer(PETS)

        # write excel file and get mailing labels
        stamp = time.strftime('%Y%m%d%H%M%S')
        out_dir = os.path.join(TEMP_FILES, 'Kennel_Permits_{}'.format(stamp))
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        # clean up???
        if CLEANUP_TEMP_FILES is True and os.path.basename(TEMP_FILES) == 'TempFiles':
            remove_files(TEMP_FILES)

        # get field filter for spreadsheet only
        fields = [f.name for f in pars_lyr.fields
                  if 'shape' not in f.name.lower()
                  and 'objectid' not in f.name.lower()
                  and f.type not in (OID, SHAPE)]

        cursor = pars_lyr.cursor(add_params=par_d)

        addresses = []

        wb = excel.ExcelWorkbook()
        ws = wb.add_sheet(headers=fields)

        # form json for pets
        feats = []
        for permit in permits.split(','):
            feats.append({'geometry': pt_geom.json,
                         'attributes': {'Owner_Name': name,
                                        'Primary_Address': address,
                                        'License': permit,
                                        'Animal_Type': 'Dog',
                                        'Date_Issued': restapi.date_to_mil(date_issued or NOW),
                                        'Date_Expired': restapi.date_to_mil(date_expired or NEXT_YEAR),
                                        'Kennel_License': kennel_license,
                }})

        add_res = pets.addFeatures(feats)

        # add kennel
        if len(feats) >= 3:
            new_kennel = {
                'geometry': pt_geom.json,
                'attributes': {
                    'Owner_Name': name,
                    'Primary_Address': address,
                    'Kennel_License': kennel_license,
                    'Status': status,
                    'Date_Issued': restapi.date_to_mil(date_issued) or NOW,
                    'Date_Expired': restapi.date_to_mil(date_expired or NEXT_YEAR)
                    }
                }

            kennel_res = kennels.addFeatures([new_kennel])

        # add rows to excel and extract addresses
        for feature in cursor.features:
            ft = feature['attributes']
            valrow = [ft[f] for f in fields]
            ws.addRow(*valrow)
            addr_list = [ft[f] for f in (TAX_NAME, TAX_ADDR, TAX_CSZ)]
            addresses.append(addr_list)

        # generate mailing labels
        pdf = os.path.join(out_dir, 'MailingLabels_avery5160.pdf')
        xls = os.path.join(out_dir, 'Kennel_Permit_Parcels.xls')
        wb.save(xls)
        mailing.avery5160(pdf, addresses)

        # export webmap
        if 'MAPLEWOOD' in address:
            a_split = address.split('MAPLEWOOD')
            address = '\r\n'.join([a_split[0], 'MAPLEWOOD' + a_split[1]])
        permit_string = '\r\n\t '.join(textwrap.wrap('Permits: ' + ', '.join(kennel_license.split(',')), 35))
        info = '\r\n'.join(['\r\n'.join(textwrap.wrap(name, 35)), address, '\r\n', permit_string])
        out_pdf = os.path.join(out_dir, 'Kennel_Permits.pdf')
        export.export_webmap(cursor.json, out_pdf, info)

        # zip folder and delete original
        zipped = zipdir(out_dir)

        #********************************************************************************************************************************
        # DELETE ME FOR MAPLEWOOD
        try:
            shutil.copy(zipped, os.path.join(r'\\arcserver3\wwwroot\TempFiles', os.path.basename(zipped)))
        except:
            pass
        #*********************************************************************************************************************************
        url = '/'.join([TEMP_FILES_URL, os.path.basename(zipped)])
        try:
            shutil.rmtree(out_dir)
        except:
            pass

        arcpy.SetParameter(8, '<a href="{}" target="_blank">Download Zip File</a>'.format(url))
        arcpy.SetParameter(9, arcpy.AsShape(json.dumps(cursor.json), True))
        return url, cursor.json

@timeit
def validate_permits():
    NOW = datetime.datetime.now()
    fs = restapi.FeatureService(PERMITS_FS)
    kennels = fs.layer(KENNELS)
    pets = fs.layer(PETS)
    chickens = fs.layer(CHICKENS)

    for lyr in (kennels, pets, chickens):
        feats = []
        fs = lyr.query(where="Date_Expired is not NULL AND Status <> 'Expired'")
        if isinstance(fs, restapi.FeatureSet):
            for ft in fs:
                if (restapi.mil_to_date(ft.get('Date_Expired')) or NOW) < NOW:
                    ft['attributes']['Status'] = 'Expired'
                    feats.append(ft.json)

        if feats:
            Message('Found {} expired permits in layer "{}"'.format(len(feats), lyr.name))
            lyr.updateFeatures(feats)
    return
