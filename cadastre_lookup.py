import urllib
import json
from urllib import request
from urllib.error import HTTPError, URLError
import socket
import ex_utilities


def prepare_uri(search_input):

    uri = 'http://services.thelist.tas.gov.au/arcgis/rest/services/Public/OpenDataWFS/MapServer/14/' + \
          'query?where=&text=&objectIds=&time=&geometry=' + str(search_input[0]) + '%2C' + str(search_input[1]) + \
          '&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelWithin&relationParam=' + \
          '&outFields=*&returnGeometry=true&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=' + \
          '&outSR=4326&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=' + \
          '&outStatistics=&returnZ=false&returnM=false&gdbVersion=&returnDistinctValues=false&resultOffset=' + \
          '&resultRecordCount=&f=pjson'

    #  print(url)  # debug
    return uri

def make_geocode_search(url):
    try:
        webURL = urllib.request.urlopen(url, timeout=10)
    except HTTPError as error:
        print('Data of %s not retrieved because %s\nURL: %s', error, url)
    except URLError as error:
        if isinstance(error.reason, socket.timeout):
            print('socket timed out - URL %s', url)
        else:
            print('some other error happened')
    else:
        #  print('Access successful.')
        data = webURL.read()
        JSON_object = json.loads(data.decode('utf-8'))
        # print(json.dumps(JSON_object, indent=2, sort_keys=True))  # debug
        feature_list = JSON_object.get('features')
        # address_item_dict = {}
        for item in feature_list:
            attributes = item.get('attributes')
            volume = attributes.get('VOLUME')
            folio = attributes.get('FOLIO')
            parcel = str(folio) + '/' + str(volume)
            geometry = item.get('geometry')
            rings = geometry.get('rings')
            flatten_rings = [num for elem in rings for num in elem]
            return flatten_rings, parcel


def main(search_input):
    url = prepare_uri(search_input)
    results = make_geocode_search(url)
    return results
