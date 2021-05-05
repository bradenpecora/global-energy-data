# This script is for compiling olddata.json into a more usable form. Outputs to newdata.json

import json, datetime, copy

def unix2year(unixtime):
    unixtime = unixtime/1000
    return datetime.datetime.utcfromtimestamp(unixtime).strftime('%Y')

def unix2year_dict(data):
    new_data = {}
    for item in data:
        date = unix2year(item["date"])
        value = item["value"]
        if value == "(s)":
            value = 0
        elif value == "--" or value == "-" or value == "NA" or value == "W":
            value = "n/a"
        new_data[date] = value
    
    return new_data

# """"
# Activity ID:
#     1: Production
#     2: Consumption

# Product ID:
#     44: Total
#     4411: Coal
#     4413: Natural Gas
#     4415: Petroleum and other liquids
#     4419: Nuclear, renewables, and others
#         4417: Nuclear
#         4418: Renewables and others
# """"
def get_activity(activity_id):
    if activity_id == 1:
        return "-PROD-"#"production"
    elif activity_id == 2:
        return "-CONS-"#"consumption"

def get_prod(prod_id):
    if prod_id == 44:
        return "TOTAL"
    elif prod_id == 4411:
        return "COAL"
    elif prod_id == 4413:
        return "NGAS" #"Natural Gas"
    elif prod_id == 4415:
        return "PETRO"#"Petroleum and other Liquids"
    elif prod_id == 4419:
        return "NUCLEAR"
    elif prod_id == 4417:
        return "NRO" #"Nuclear, Renewables and Others"
    elif prod_id == 4418:
        return "RENEW" #"Renewables and Others"

def main():

    with open('olddata.json','r') as f:
        data_in = json.load(f)

    countries = {}

    length = range(len(data_in))

    for i in length:
        name = data_in[i]["iso"]

        if name == "WORL":
            name = "WOR"

        activity = get_activity(data_in[i]["activityid"])
        product = get_prod(data_in[i]["productid"])
        idstring = name + activity + product
        this_data = unix2year_dict(data_in[i]["data"])

        countries[idstring] = this_data

    with open('newdata.json', 'w') as f:
        json.dump(countries, f, indent=2)

if __name__ == "__main__":
    main()