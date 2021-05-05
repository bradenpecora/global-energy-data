# api.py
import json
from flask import Flask, request, jsonify
from jobs import add_job, rd 
from data import get_keys

app = Flask(__name__)

@app.route('/',methods=['GET'])
def instructions():
    return """
    The following are the routes for this API

    /                      lists possible routes
    /help                  describes data terminology
    /reset                 clears and (re)loads original data to db

    The following routes have required query pararemeters. Hitting the route without a query will describe the parameters.

    /get/all               Gets all data for specified keys (country name, activity type, product type)
    /get/date              Gets all data for specified keys for given year
    /get/date_range        Gets all data for specified keys for given year range

    /update                Change or add a new year-value pair to a specific ISO-ACTT-PRODT

    /create                Add a new ISO-ACTT-PROT. Use /update to add values

    /delete/all            Deletes all data for specified keys (country name, activity type, product type)
    /delete/date           Deletes all data for specified keys for given year
    /delete/date_range     Deletes all data for specified keys for given year range




"""

@app.route('/help',methods=['GET'])
def help_me():
    return """
    This database/API system contains international energy data sourced from the U.S. Energy Information Administration (eia.gov)

    Data is stored in the database using hashes the follow the following "Key:Value" format:

    -Key: "ISO-ACTT-PRODT"
        -Type is string
        -ISO is the three letter 'ISO 3155-1 alpha-3' uppercase country code. 
            The current codes can be found here: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3
        -ACTT is the activity type. The values are either PROD for prodcution or CONS for consumption
        -PRODT is the product type. The values can be
                - "TOTAL"
                - "COAL"
                - "NGAS" for Natural Gas
                - "PETRO" for Petroleum and other Liquids
                - "NUCLEAR"
                - "NRO" for Nuclear, Renewables and Others
                - "RENEW" for Renewables and Others


    -Value: {
            "YEAR1": Value 1,
            .
            .
            "YEARn": Value n
            } 
        - Type is dictionary
        - "YEAR" is a string containing the four digit year, i.e. "1991". Data is included from 1980 to 2018
        - "Value" is a floating point number containing the amount of product either consumed or produced by the country.
                The units are quad BTU.


"""

@app.route('/reset')
def reset_data():
    
    for key in rd.keys():
        rd.delete(key)
    
    with open('data/newdata.json','r') as f:
        data = json.load(f)

    for key in data:
        rd.hmset(key, data[key])

    return "Data reset \n"

@app.route('/test')
def test():
    return json.dumps(rd.hget("YUG-PROD-TOTAL", "1991"))


@app.route('/get/all', methods=['GET'])
def get_from_string():
    
    iso = str(request.args.get('iso')).upper()
    actt = str(request.args.get('actt')).upper()
    prodt = str(request.args.get('prodt')).upper()

    if iso == 'NONE' and actt == 'NONE' and prodt == 'NONE':
        return """
    This is a route for reading each year's data for an inputted country code (iso), activity (actt), product (prodt),
    or any combination of those three parameters. Use the form:

    curl '<host ip>:/<flask port>/get/all?param1=VALUE1&param2=VALUE2&param3=VALUE3'

    Each 'param' can be either:
    -'iso'   : Value will be ISO alpha-3 country code (https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3)
    -'actt'  : Value will be the activity type. (PROD for production, CONS for consumption)
    -'prodt' : Value will be the product type. See /help route for more.
"""
    else:
        keys = get_keys(iso, actt, prodt)
        output = {}
        for key in keys:
            output[key] = rd.hgetall(key)

        return jsonify(output)

@app.route('/get/date', methods=['GET'])
def get_from_date():
    
    iso = str(request.args.get('iso')).upper()
    actt = str(request.args.get('actt')).upper()
    prodt = str(request.args.get('prodt')).upper()
    year = str(request.args.get('year'))

    if iso == 'NONE' and actt == 'NONE' and prodt == 'NONE' or year == 'None':
        return """
    This is a route for reading each year's data for an inputted country code (iso), activity (actt), product (prodt),
    or any combination of those three parameters. Use the form:

    curl '<host ip>:/<flask port>/get/date?param1=VALUE1&param2=VALUE2&param3=VALUE3'

    Each 'param' can be either:
    -'iso'   : Value will be ISO alpha-3 country code (https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3)
    -'actt'  : Value will be the activity type. (PROD for production, CONS for consumption)
    -'prodt' : Value will be the product type. See /help route for more.
    -'year'  : Value will be the four digit year the user wishes to find data for. This is NECESSARY.

"""
    else:
        keys = get_keys(iso, actt, prodt)
        output = {}
        for key in keys:
            output[key] = {year : rd.hget(key, year)}

        return jsonify(output)

@app.route('/get/date_range', methods=['GET'])
def get_from_date_range():
    
    iso = str(request.args.get('iso')).upper()
    actt = str(request.args.get('actt')).upper()
    prodt = str(request.args.get('prodt')).upper()
    year1 = str(request.args.get('year1'))
    year2 = str(request.args.get('year2'))


    if iso == 'NONE' and actt == 'NONE' and prodt == 'NONE' or year1 == 'None' or year2 == 'None':
        return """
    This is a route for reading each year's data for an inputted country code (iso), activity (actt), product (prodt),
    or any combination of those three parameters. Use the form:

    curl '<host ip>:/<flask port>/get/date_range?param1=VALUE1&param2=VALUE2&param3=VALUE3'

    Each 'param' can be either:
    -'iso'   : Value will be ISO alpha-3 country code (https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3)
    -'actt'  : Value will be the activity type. (PROD for production, CONS for consumption)
    -'prodt' : Value will be the product type. See /help route for more.
    -'year1'  : Value will be the lower bound four digit year the user wishes to find data for. This is NECESSARY.
    -'year2'  : Value will be the upper bound four digit year the user wishes to find data for. This is NECESSARY.

"""
    else:

        year1 = int(year1)
        year2 = int(year2)

        if year2 < year1:
            temp_year = year1
            year1 = year2
            year2 = temp_year

        keys = get_keys(iso, actt, prodt)
        output = {}

        for key in keys:
            year_dict = {}
            for year in range(year1, year2 + 1):
                year_dict[year] = rd.hget(key, year)
            output[key] = year_dict

        return jsonify(output)

@app.route('/update', methods=['GET'])
def update_value():
    
    iso = str(request.args.get('iso')).upper()
    actt = str(request.args.get('actt')).upper()
    prodt = str(request.args.get('prodt')).upper()
    year = str(request.args.get('year'))
    value = str(request.args.get('value'))

    if iso == 'NONE' or actt == 'NONE' or prodt == 'NONE' or year == 'None' or value == 'None':
        return """
    This is a route for updating each a specific year's value for a ISO-ACTT-PRODT.

    curl '<host ip>:/<flask port>/get/date?iso=ISO&actt=ACTT&prodt=PRODT&year=YEAR&value=VALUE'

    Each 'param' can be either:
    -'iso'   : ISO will be ISO alpha-3 country code (https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3)
    -'actt'  : ACTT will be the activity type. (PROD for production, CONS for consumption)
    -'prodt' : PRODT will be the product type. See /help route for more.
    -'year'  : YEAR will be the four digit year the user wishes to update (or add) data for.
    -'value' : VALUE will be the new assigned value for YEAR.

"""
    else:
        key = get_keys(iso, actt, prodt)[0]
        rd.hset(key, int(year), float(value))

        output = key + year + "=" + value + "\n"

        return output

@app.route('/create', methods=['GET','POST'])
def create_data():
    if request.method == 'POST':
        try:
            in_data = request.get_json(force=True)
        except Exception as e:
            return True, json.dumps({'status': "Error", 'message': 'Invalid JSON: {}.'.format(e)})
        rd.hmset(in_data[country], in_data[data])
        return "The following data has created: \n" + json.dumps({in_data[country]: in_data[data]}) + "\n"

    else:
        return """
    A new set of data can be created with the following route:

        curl -X POST -H "content-type: application/json" -d '{"country": "ISO-ACTT-PRODT", "data": {"year1": value1, "year2": value2, "yearN": valueN}}

    "ISO-ACTT-PRODT" is the format for the country identifer. Technically, this could be anything, 
    but ISO must remain three characters and ACTT must remain four.
    See /help for more info on these parameters.

"""

@app.route('/delete/all', methods=['GET'])
def delete_from_string():
    
    iso = str(request.args.get('iso')).upper()
    actt = str(request.args.get('actt')).upper()
    prodt = str(request.args.get('prodt')).upper()

    if iso == 'NONE' and actt == 'NONE' and prodt == 'NONE':
        return """
    This is a route for deleting each year's data for an inputted country code (iso), activity (actt), product (prodt),
    or any combination of those three parameters. Use the form:

    curl '<host ip>:/<flask port>/delete/all?param1=VALUE1&param2=VALUE2&param3=VALUE3'

    Each 'param' can be either:
    -'iso'   : Value will be ISO alpha-3 country code (https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3)
    -'actt'  : Value will be the activity type. (PROD for production, CONS for consumption)
    -'prodt' : Value will be the product type. See /help route for more.
"""
    else:
        keys = get_keys(iso, actt, prodt)
        for key in keys:
            rd.delete(key)

        output = "The following keys were deleted: \n" + str(keys)

        return output

@app.route('/delete/date', methods=['GET'])
def delete_from_date():
    
    iso = str(request.args.get('iso')).upper()
    actt = str(request.args.get('actt')).upper()
    prodt = str(request.args.get('prodt')).upper()
    year = str(request.args.get('year'))

    if iso == 'NONE' and actt == 'NONE' and prodt == 'NONE' or year == 'None':
        return """
    This is a route for deleting each year's data for an inputted country code (iso), activity (actt), product (prodt),
    or any combination of those three parameters. Use the form:

    curl '<host ip>:/<flask port>/delete/date?param1=VALUE1&param2=VALUE2&param3=VALUE3'

    Each 'param' can be either:
    -'iso'   : Value will be ISO alpha-3 country code (https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3)
    -'actt'  : Value will be the activity type. (PROD for production, CONS for consumption)
    -'prodt' : Value will be the product type. See /help route for more.
    -'year'  : Value will be the four digit year the user wishes to delete data for. This is NECESSARY.

"""
    else:
        keys = get_keys(iso, actt, prodt)
        for key in keys:
            rd.hdel(key, year)

        output = "The data for " + year + " was deleted for the following keys: \n" + str(keys)

        return output

@app.route('/delete/date_range', methods=['GET'])
def delete_from_date_range():
    
    iso = str(request.args.get('iso')).upper()
    actt = str(request.args.get('actt')).upper()
    prodt = str(request.args.get('prodt')).upper()
    year1 = str(request.args.get('year1'))
    year2 = str(request.args.get('year2'))


    if iso == 'NONE' and actt == 'NONE' and prodt == 'NONE' or year1 == 'None' or year2 == 'None':
        return """
    This is a route for reading each year's data for an inputted country code (iso), activity (actt), product (prodt),
    or any combination of those three parameters. Use the form:

    curl '<host ip>:/<flask port>/delete/date_range?param1=VALUE1&param2=VALUE2&param3=VALUE3'

    Each 'param' can be either:
    -'iso'   : Value will be ISO alpha-3 country code (https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3)
    -'actt'  : Value will be the activity type. (PROD for production, CONS for consumption)
    -'prodt' : Value will be the product type. See /help route for more.
    -'year1'  : Value will be the lower bound four digit year the user wishes to delete data for. This is NECESSARY.
    -'year2'  : Value will be the upper bound four digit year the user wishes to delete data for. This is NECESSARY.

"""
    else:

        year1 = int(year1)
        year2 = int(year2)

        if year2 < year1:
            temp_year = year1
            year1 = year2
            year2 = temp_year

        keys = get_keys(iso, actt, prodt)

        for key in keys:
            for year in range(year1, year2 + 1):
                rd.hdel(key, year)

        output = "The data for " + year1 + " through " + year2 + " was deleted for the following keys: \n" + str(keys)

        return output

@app.route('/jobs', methods=['GET','POST'])
def jobs_api():
    if request.method == 'POST':
        try:
            job = request.get_json(force=True)
        except Exception as e:
            return True, json.dumps({'status': "Error", 'message': 'Invalid JSON: {}.'.format(e)})
        return "The following job has been submitted: \n" + json.dumps(add_job(job['start'], job['end'])) + "\n"

    else:
        return """
    Add information on POSTing a job
"""

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')