import urllib
import json
from urllib import request
from urllib.error import HTTPError, URLError
import socket
import ex_utilities


class Address:
    def __init__(self):
        self.locality = ''
        self.streetName = ''
        self.streetType = ''
        self.streetNumber = ''
        self.postcode = ''
        self.x = -1.0
        self.y = -1.0

    def clear(self):
        self.locality = ''
        self.streetName = ''
        self.streetType = ''
        self.streetNumber = ''
        self.postcode = ''
        self.x = -1.0
        self.y = -1.0

    def toString(self):
        return self.streetNumber + ' ' + self.streetName + ' ' + self.streetType + ', ' + self.locality

    def getCoords(self):
        return self.x, self.y

    def locality_only(self):
        return self.locality != '' and self.streetNumber == '' and self.streetName == '' and self.streetType == ''

    def street_only(self):
        return self.locality == '' and self.streetNumber == '' and self.streetName != '' and self.streetType != ''


input_string = ''
parsed_address = Address()
tokenised_string = []


def set_variables(search_input):
    input_string = search_input
    global tokenised_string
    tokenised_string = ex_utilities.clean_string(input_string)


def parse_street_type():
    street_types = ex_utilities.street_type_list()
    street_abbreviations = ex_utilities.street_contraction_list()
    for index, entry in enumerate(tokenised_string):
        if entry in street_types:
            parsed_address.streetType = entry
            return index
        elif entry in street_abbreviations:
            abbreviations_map = ex_utilities.contraction_map()
            parsed_address.streetType = abbreviations_map.get(entry)
            return index
    return 0


def parse_locality(position):
    l_locality = ''
    for index, entry in enumerate(tokenised_string):
        if position == 0 or index > position:
            l_locality += entry + ' '
    parsed_address.locality = l_locality.strip()


def parse_street_name(position):
    street_name = ''
    for index, entry in enumerate(tokenised_string):
        if not ex_utilities.contains_digit(entry) and index < position and not entry.upper() == "UNIT":
            street_name += entry + ' '
    parsed_address.streetName = street_name.strip()


def parse_street_number(position):
    for index, entry in enumerate(tokenised_string):
        if entry.isdigit() and index < position:
            parsed_address.streetNumber = entry


def parse_address():
    contains_road = parse_street_type()
    parse_locality(contains_road)
    if contains_road > 0:
        parse_street_name(contains_road)
        parse_street_number(contains_road)


def prepare_url():
    parse_address()
    #  print(parsed_address)
    if parsed_address.locality_only():
        locality = 'LOCALITY%3D%27' + parsed_address.locality + '%27'
    else:
        locality = 'LOCALITY%3D%27' + parsed_address.locality + '%27+AND+' if parsed_address.locality != '' else ''
    streetName = 'STREET%3D%27' + parsed_address.streetName + '%27+AND+' if parsed_address.streetName != '' else ''
    if parsed_address.street_only():
        streetType = 'ST_TYPE%3D%27' + parsed_address.streetType + '%27'
    else:
        streetType = 'ST_TYPE%3D%27' + parsed_address.streetType + '%27+AND+' if parsed_address.streetType != '' else ''
    streetNumber = 'ST_NO_FROM%3D' + parsed_address.streetNumber if parsed_address.streetNumber != '' else ''

    url = ('https://services.thelist.tas.gov.au/arcgis/rest/services/Public/' +
           'CadastreAndAdministrative/MapServer/43/query?where=' +
           locality + streetName + streetType + streetNumber +
           '&text=&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&' +
           'spatialRel=esriSpatialRelIntersects&relationParam=&outFields=ST_NO_FROM%2C+' +
           'STREET%2C+ST_TYPE%2C+LOCALITY%2C+POSTCODE&returnGeometry=' +
           'true&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR=4326&' +
           'returnIdsOnly=false&returnCountOnly=false&orderByFields=&' +
           'groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&' +
           'gdbVersion=&returnDistinctValues=false&resultOffset=&resultRecordCount=&f=json')
    #  print(url)  # debug
    return url


def process_item(item):
    new_address = Address()
    attributes = item.get('attributes')
    new_address.locality = attributes.get('LOCALITY')
    new_address.streetName = attributes.get('STREET')
    new_address.streetType = attributes.get('ST_TYPE')
    new_address.streetNumber = str(attributes.get('ST_NO_FROM'))
    new_address.postcode = str(attributes.get('POSTCODE'))
    geometry = item.get('geometry')
    new_address.x = geometry.get('x')
    new_address.y = geometry.get('y')
    return new_address


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
        #  print(json.dumps(JSON_object, indent=2, sort_keys=True))  # debug
        feature_list = JSON_object.get('features')
        address_item_dict = {}
        for item in feature_list:
            address = process_item(item)
            address_item_dict[address.toString()] = address.getCoords()
        return address_item_dict


def main(search_input):
    parsed_address.clear()
    set_variables(search_input)
    parse_address()
    url = prepare_url()
    results = make_geocode_search(url)
    return results
