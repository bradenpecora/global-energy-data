# api.py
import json
from flask import Flask, request, jsonify, send_file
from jobs import add_job, rd, jrd, image_rd
from data import get_keys

app = Flask(__name__)

@app.route('/',methods=['GET'])
def instructions():
    return """
    The following are the routes for this API

    /                      lists possible routes
    /help                  describes data terminology
    /reset                 clears and (re)loads original data to db
                            - This should be run on initial start up.
    /clear/all             clears all databases
    /clear/data            clears database containing energy data
    /clear/jobs            clears database containing job data
    /clear/images          clears database containing image file data

    The following routes have required query pararemeters. Hitting the route without a query will describe the parameters.

    /get/all               Gets all data for specified keys (country name, activity type, product type)
    /get/date              Gets all data for specified keys for given year
    /get/date_range        Gets all data for specified keys for given year range

    /update                Change or add a new year-value pair to a specific ISO-ACTT-PRODT

    /create                Add a new ISO-ACTT-PROT with empty data.

    /delete/all            Deletes all data for specified keys (country name, activity type, product type)
    /delete/date           Deletes all data for specified keys for given year
    /delete/date_range     Deletes all data for specified keys for given year range

    /jobs                  Find data for a specific job
    /jobs/all              Prints all jobs and data
    /graph                 Used for instructing worker to create a graph
    /get_image             Save an image produced by a job


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
    """ Deletes data from rd and reloads from json file """

    for key in rd.keys():
        rd.delete(key)
    
    with open('data/newdata.json','r') as f:
        data = json.load(f)

    for key in data:
        rd.hmset(key, data[key])

    return "Data reset \n"

@app.route('/clear/data')
def clear_data():
    """ Deletes data from rd """

    for key in rd.keys():
        rd.delete(key)

    return "Data cleared \n"

@app.route('/clear/jobs')
def clear_jobs():
    """ Deletes data from jrd """

    for key in jrd.keys():
        jrd.delete(key)

    return "Jobs cleared \n"

@app.route('/clear/images')
def clear_image():
    """ Deletes data from image_rd """

    for key in image_rd.keys():
        image_rd.delete(key)

    return "Images cleared \n"

@app.route('/clear/all')
def clear_all():
    """Deletes all data from all datebases"""
    clear_data()
    clear_jobs()
    clear_image()

    return "All databases cleared \n"

@app.route('/get/all', methods=['GET'])
def get_from_string():
    
    iso = str(request.args.get('iso')).upper()
    actt = str(request.args.get('actt')).upper()
    prodt = str(request.args.get('prodt')).upper()

    if iso == 'NONE' and actt == 'NONE' and prodt == 'NONE':
        return """
    This is a route for reading each year's data for an inputted country code (iso), activity (actt), product (prodt),
    or any combination of those three parameters. At least one parameter must be specified. If a parameter is not specified,
    all data that matches the other parameters will be returned.
     Use the form:

    curl '<host ip>:<flask port>/get/all?param1=VALUE1&param2=VALUE2&param3=VALUE3'

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
    or any combination of those three parameters. At least two parameter must be specified (one must be 'year'). 
    If a parameter is not specified, all data that matches the other parameters will be returned.
    Use the form:

    curl '<host ip>:<flask port>/get/date?param1=VALUE1&param2=VALUE2&param3=VALUE3&year=YEAR'

    Each 'param' can be either:
    -'iso'   : Value will be ISO alpha-3 country code (https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3)
    -'actt'  : Value will be the activity type. (PROD for production, CONS for consumption)
    -'prodt' : Value will be the product type. See /help route for more.
    -'year'  : Value will be the four digit year the user wishes to find data for. 
            -This is a required parameter

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
    or any combination of those three parameters. If a parameter is not specified, all data that matches the other parameters will be returned.
     Use the form:

    curl '<host ip>:<flask port>/get/date_range?param1=VALUE1&param2=VALUE2&param3=VALUE3&year1=YEAR1&year2=YEAR2'

    Each 'param' can be either:
    -'iso'   : Value will be ISO alpha-3 country code (https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3)
    -'actt'  : Value will be the activity type. (PROD for production, CONS for consumption)
    -'prodt' : Value will be the product type. See /help route for more.
    -'year1' : Value will be the lower bound four digit year the user wishes to find data for. 
                -This is a required parameter.
    -'year2' : Value will be the upper bound four digit year the user wishes to find data for. 
                -This is a required parameter.

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
    This is a route for updating each a specific year's value for a ISO-ACTT-PRODT. All parameters are required.

    curl '<host ip>:<flask port>/get/date?iso=ISO&actt=ACTT&prodt=PRODT&year=YEAR&value=VALUE'

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

        output = key + ":" + year + "=" + value + "\n"

        return output

@app.route('/create', methods=['GET','POST'])
def create_data():
    if request.method == 'POST':
        try:
            in_data = request.get_json(force=True)
        except Exception as e:
            return True, json.dumps({'status': "Error", 'message': 'Invalid JSON: {}.'.format(e)})
        rd.hmset(in_data['country'], in_data['data'])
        return "The following data has created: \n" + json.dumps({in_data['country']: in_data['data']}) + "\n"

    else:
        return """
    A new set of data can be created with the following route:

        curl -X POST -H "content-type: application/json" -d '{"country": "ISO-ACTT-PRODT", "data": {"year1": value1, "year2": value2, "yearN": valueN}}' <flask IP>:<flask port>/create

    "ISO-ACTT-PRODT" is the format for the country identifer. Technically, this could be anything, 
    but ISO must remain three characters and ACTT must remain four.
    See /help for more info on/definition of these parameters.

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

    curl '<host ip>:<flask port>/delete/all?param1=VALUE1&param2=VALUE2&param3=VALUE3'

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

    curl '<host ip>:<flask port>/delete/date?param1=VALUE1&param2=VALUE2&param3=VALUE3'

    Each 'param' can be either:
    -'iso'   : Value will be ISO alpha-3 country code (https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3)
    -'actt'  : Value will be the activity type. (PROD for production, CONS for consumption)
    -'prodt' : Value will be the product type. See /help route for more.
    -'year'  : Value will be the four digit year the user wishes to delete data for. 
                - This is a required parameter.

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

    curl '<host ip>:<flask port>/delete/date_range?param1=VALUE1&param2=VALUE2&param3=VALUE3'

    Each 'param' can be either:
    -'iso'   : Value will be ISO alpha-3 country code (https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3)
    -'actt'  : Value will be the activity type. (PROD for production, CONS for consumption)
    -'prodt' : Value will be the product type. See /help route for more.
    -'year1'  : Value will be the lower bound four digit year the user wishes to delete data for. 
                - This is a required parameter.
    -'year2'  : Value will be the upper bound four digit year the user wishes to delete data for. 
                - This is a required parameter.

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

        output = "The data for " + str(year1) + " through " + str(year2) + " was deleted for the following keys: \n" + str(keys)

        return output

@app.route('/graph', methods=['GET','POST'])
def jobs_api_graph():
    if request.method == 'POST':
        try:
            job = request.get_json()
        except Exception as e:
            return json.dumps({'status': "Error", 'message': 'Invalid JSON: {}.'.format(e)})

        countries = json.dumps(job['countries'])
        date_range = json.dumps(job['date_range'])

        return jsonify(add_job(countries, date_range))
    else:
        return """
    Data can be plotted with the following route:

        curl -X POST -H "content-type: application/json" -d '{"countries": [{"iso": "ISO1", "actt": "ACTT", "prodt": "PRODT"}, {<next dict>}], "date_range": [YEAR1, YEAR2]}' <flask IP>:<flask port>/graph

    Each dictionary in the list corresponding to the "countries" key must have at least one entry (iso, actt, prodt).
    If a parameter is not specified, all ISO-ACTT-PRODT with matching values will be selected. For example, if ISO and PRODT are specified,
    but ACTT is not, all ACTT types that match the ISO and PRODT will be plotted.
    Additional sets of countries can be added to the graph with additional dictionaries in the list.

    The date range is specified by YEAR1 and YEAR2. All years between these years will be plotted, if the datapoint exists. 

    Use /jobs to check stauts of the job posted
    Use /get_image to download the image after it has been created.

"""

@app.route('/jobs', methods=['GET'])
def get_job():
    jid = str(request.args.get('jid'))
    if jid != 'None':
        jid = 'job.{}'.format(jid)
        output = jrd.hgetall(jid)
        return jsonify(output)
    else:
        return """
    This route can be used to find the status of a specific job.

        curl '<flask IP>:<flask port>/jobs?jid=<job id>

"""

@app.route('/jobs/all', methods=['GET'])
def get_jobs_all():
    """Prints all jobs"""
    output = {}
    for jid in jrd.keys():
        output[jid] = jrd.hgetall(jid)
    return jsonify(output)


@app.route('/get_image', methods=['GET'])
def get_image():
    jid = str(request.args.get('jid'))
    if jid != 'None':
        path = f'{jid}.png'
        with open(path, 'wb') as f:
            f.write(image_rd.hget(jid, 'image'))
        return send_file(path, mimetype='image/png', as_attachment=True)
    else:
        return """
    This route can be used to download an image 

        curl '<flask IP>:<flask port>/get_image?jid=<job id> > <filename>.png

    Notice the `>` used not as a marker for substitution, which is used to output the response (containing the image).
"""

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')