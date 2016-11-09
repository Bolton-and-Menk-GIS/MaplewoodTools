#-------------------------------------------------------------------------------
# Name:        module2
# Purpose:
#
# Author:      calebma
#
# Created:     23/05/2016
# Copyright:   (c) calebma 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
GOOGLE = 'http://maps.googleapis.com/maps/api/geocode/json?'
RAMSEY_GC = 'https://maps.co.ramsey.mn.us/arcgis/rest/services/Services/RCGeocoder_PlaceAddress/GeocodeServer'
ZONING = 'http://gis.maplewoodmn.gov/arcgis/rest/services/Projects/Zoning/MapServer'
RAMSEY_MS = 'https://maps.co.ramsey.mn.us/arcgis/rest/services/MapRamsey/MapRamseyOperationalLayersAll/MapServer'
ZONE_LAYER = 'Zoning Classifications'
PARCEL_LAYER = 'Parcels'

# Permits Feature Service
PERMITS_FS = 'http://gis.bolton-menk.com/bmigis/rest/services/MPWD/Permits/FeatureServer'
CHICKENS = 'Chickens'
KENNELS = 'Kennels'
PETS = 'Pets'
DANGEROUS_DOGS = 'Dangerous Dog'

# Mailing info fields
TAX_NAME = 'TaxPayerName'
TAX_ADDR = 'PrimaryTaxAddress'
TAX_CSZ = 'PrimaryTaxCityStateZIP'

# ramsey wkid
RAMSEY_WKID = 103768

# temp directory location
TEMP_FILES = r'\\arcserver2\wwwroot\TempFiles'
TEMP_FILES_URL = 'http://gis.bolton-menk.com/TempFiles'

# misc
CLEANUP_TEMP_FILES = True