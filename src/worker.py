from jobs import q, rd, update_job_status, get_job_data, add_image
from data import get_keys
import time
import os
import matplotlib.pyplot as plt
import json

worker_ip = os.environ.get('WORKER_IP')

def get_field(field, fields_dict):
    if field in fields_dict:
        return str(fields_dict[field]).upper()
    else:
        return "NONE"    

@q.worker
def create_graph(jid):
    update_job_status(jid, 'in progress')
    job_data = get_job_data(jid)

    date_range = json.loads(job_data['date_range']) # is a string. Needs to be ints
    year_low = int(date_range[0])
    year_high = int(date_range[1])
    if year_high < year_low:
        temp = year_low
        year_low = year_high
        year_high = temp 
    years = range(year_low, year_high+1)

    keys = []

    countries = json.loads(job_data['countries'])

    for fields_dict in countries:

        iso = get_field("iso", fields_dict)
        actt = get_field("actt", fields_dict)
        prodt = get_field("prodt", fields_dict)

        partial_keys = get_keys(iso,actt,prodt)
        print(partial_keys)
        for key in partial_keys:
            keys.append(key)

    print(keys)

    for key in keys:
        values = []
        available_years = []
        for year in years:
            value = rd.hget(key,year)
            print(value)
            if value != "n/a" and value is not None:
                values.append(float(value))
                available_years.append(int(year))
            
        print(str(values))
        print(str(available_years))
        plt.plot(available_years, values, label = key)

    plt.xlabel('Year')
    plt.ylabel('Value (quad BTU)')
    plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
    plt.tight_layout()
    plt.show()

    plt.savefig('/line_plot.png')

    with open('/line_plot.png', 'rb') as f:
        img = f.read()

    add_image(jid, img)

    plt.clf()

    update_job_status(jid, 'complete')

create_graph()