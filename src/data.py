from jobs import rd

def _find_by_iso(in_string):
    """
    Returns a list of all keys (from "data" database) that match in_string for the length of in_string

    Input: Any of the following
    in_string = "ISO" returns all keys with matching country abbreviation (ISO)
    in_string = "ISO-ACTT" returns all keys with matching ISO and activity type (either PROD or CONS)
    in_string = "ISO-ACTT-PRODT" returns keys with matching ISO, activity type, and product type (TOTAL, NG, COAL, etc.)
    """

    keys = []

    for key in rd.keys():
        if key[0:len(in_string)] == in_string:
            keys.append(key)

    return keys

def _find_by_actt(in_string):
    """
    Returns a list of all the keys (from "data" database) with a given ACTT (activity type) abbreviation. Product type can be appended

    Input: Any of the following
    in_string = "ACTT" returns all keys with matching activity (ACTT: either PROD or CONS) type
    in_string = "ACTT-PRODT" returns all keys with matching activity and product type (TOTAL, NG, COAL, etc.)
    """

    keys = []

    for key in rd.keys():
        if key[4:4+len(in_string)] == in_string:
            keys.append(key)

    return keys

def _find_by_prodt(in_string):
    """
    Returns a list of all keys (from "data" database) with inputted PRODT (product type) abbreviation (both production and consumption).

    Input:
    in_string = "PRODT"

    "PRODT" options:
    "TOTAL" = total energy
    "COAL" = coal
    "NGAS" = natural gas
    "PETRO" = petroleum and other liquids
    "NUCLEAR" = nuclear
    "NRO" = nuclear, renewables and others
    "RENEW" = Renewables and others
    """

    keys = []

    for key in rd.keys():
        if key[9:9+len(in_string)] == in_string:
            keys.append(key)

    return keys
    
def _find_by_iso_and_prodt(in_string):
    """
    Returns a list of all keys (from "data" database) with inputted PRODT (product type) abbreviation (both production and consumption).

    Input:
    in_string = "ISO-PRODT"
    """

    keys = []

    for key in rd.keys():
        if key[0:3] == in_string[0:3] and key[9:5+len(in_string)] == in_string[4:len(in_string)]:
            keys.append(key)

    return keys

def get_keys(iso, actt, prodt):
    """
    Returns list of keys (from "data" database) by iso (country abbreviation), actt (activity type abbv.) and prodt (product type abbv.)
    Input 'NONE' for a parameter that is not specified.
    """
    if iso == 'NONE' and actt == 'NONE' and prodt == 'NONE':
        raise Exception
    elif iso == 'NONE':
        if actt == 'NONE':
            keys = _find_by_prodt(prodt)
        else:
            if prodt == 'NONE':
                keys = _find_by_actt(actt)
            else:
                in_string = actt + "-" + prodt
                keys = _find_by_actt(in_string)
    else:   
        if actt == 'NONE':
            if prodt != 'NONE':
                in_string = iso + "-" + prodt
                keys = _find_by_iso_and_prodt(in_string)
            else:
                keys = _find_by_iso(iso)
        else:
            if prodt == 'NONE':
                in_string = iso + "-" + actt
                keys = _find_by_iso(in_string)
            else:
                in_string = iso + "-" + actt + "-" + prodt
                keys = _find_by_iso(in_string)

    return keys
