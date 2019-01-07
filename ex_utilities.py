import re


def clean_string(raw_string):
    cleaned_string = re.sub('[^A-Za-z0-9 /-]+', '', raw_string)
    tokens = ' '.join(cleaned_string.split()).upper().split(' ')
    return tokens


def street_type_list():
    return ["ALLEY", "ARCADE", "AVENUE", "BOULEVARD", "BYPASS", "CIRCUIT", "CLOSE", "CORNER", "COURT",
            "CRESCENT", "CUL-DE-SAC", "DRIVE", "ESPLANADE", "GREEN", "GROVE", "HIGHWAY", "JUNCTION",
            "LANE", "LINK", "MEWS", "PARADE", "PLACE", "RIDGE", "ROAD", "SQUARE", "STREET", "TERRACE", "WAY"]


def street_contraction_list():
    return ["ALLY", "AL", "ARC", "AVE", "AV", "BVD", "BVDE", "BYPA", "BY", "BYP", "CCT", "CL", "CRN", "CT",
            "CRES", "CR", "CDS", "DR", "ESP", "GRN", "GR", "HWY", "JNC", "JC", "JN", "LN", "LNE", "LNK", "MEWS",
            "PDE", "PD", "PL", "PLC", "RDGE", "RD", "SQ", "ST", "STR", "TCE", "WY", "W"]


def contraction_map():
    contractions = {
        "ALLY": "ALLEY",
        "AL": "ALLEY",
        "ARC": "ARCADE",
        "AVE": "AVENUE",
        "AV": "AVENUE",
        "BVD": "BOULEVARD",
        "BVDE": "BOULEVARD",
        "BYPA": "BYPASS",
        "BY": "BYPASS",
        "BYP": "BYPASS",
        "CCT": "CIRCUIT",
        "CL": "CLOSE",
        "CRN": "CORNER",
        "CT": "COURT",
        "CRES": "CRESCENT",
        "CR": "CRESCENT",
        "CDS": "CUL-DE-SAC",
        "DR": "DRIVE",
        "ESP": "ESPLANADE",
        "GRN": "GREEN",
        "GR": "GROVE",
        "HWY": "HIGHWAY",
        "JNC": "JUNCTION",
        "JC": "JUNCTION",
        "JN": "JUNCTION",
        "LN": "LANE",
        "LNE": "LANE",
        "LNK": "LINK",
        "MEWS": "MEWS",
        "PDE": "PARADE",
        "PD": "PARADE",
        "PL": "PLACE",
        "PLC": "PLACE",
        "RDGE": "RIDGE",
        "RD": "ROAD",
        "SQ": "SQUARE",
        "ST": "STREET",
        "STR": "STREET",
        "TCE": "TERRACE",
        "WY": "WAY",
        "W": "WAY"
    }
    return contractions


def contains_digit(s):
    return any(i.isdigit() for i in s)
