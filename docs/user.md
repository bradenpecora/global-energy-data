# Interacting with the App

The files assumes that the system is either deployed with Docker or Kubernetes. See `deploy.md` for deployment instructions.

 If Docker containers are used for the system, the host IP will be `localhost` and the flask port will be `5026`, unless this was changed in the Makefile. Curl requests can be sent from the local machine.
 ```bash
[local] $ curl localhost:5026/<route>
 ```

 If Kubernetes is used for the system, the host IP will be the IP of the flask service (`kubectl get services`) and the flask port will be `5000`. The system can be interacted with through `exec`ing into a Kubernetes pod in the same cluster.
 ```bash
 [debug] $ curl <Flask Service IP>:5000/<route>
 ```

 As of publishing, this system is connected to the internet with the following address 
 ```
 https://isp-proxy.tacc.utexas.edu/bradenp/<route>
```

Substitute in the proper information when interacting with the system. Examples are given from a k8s, mostly.

## Terminology

This data set contains the amount of energy either produced or consumed in quad BTU. The data is organized by country, activity type, and product type.

This system uses three letter uppercase ISO codes for country, which can be found [here](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3). `WOR` refers to the data for the world.

 Lowercase `"iso"` refers to that literal string itself, while uppercase `'ISO'` should be substituted for a specific country ISO. A key value pair could look like `{'iso': 'USA'}`, where '`'USA'` is the `'PRODT'` for the United States. Custom `'ISO'`s can be used, but they must remain three uppercase characters.

Activity type is abbreviated to `actt`. The above lowercase/uppercase convention applies. `ACTT` is either `PROD` for production or `CONS` for consumption. Additional `ACTT` can be created, but they must remain four uppercase characters.

Product type is abbreviated to `prodt` and also follows the same casing convention. The current values are as follows, but the system can handle additional `'PRODT'`s.
- "TOTAL"
- "COAL"
- "NGAS" for Natural Gas
- "PETRO" for Petroleum and other Liquids
- "NUCLEAR"
- "NRO" for Nuclear, Renewables and Others
- "RENEW" for Renewables and Others

Thus, a key takes the form `"ISO-ACTT-PRODT"`. As a group, we will call the ISO, activity type, and product type as the "ckey params" for country key parameters.

# Routes

The following are the routes for the system with examples when applicable.

## Query-less Routes
The following routes are for information, or resetting/clearing data from the databases.
```
/                      lists possible routes
/help                  describes data terminology
/reset                 clears and (re)loads original data to db
                        - This should be run on initial start up.
/clear/all             clears all databases
/clear/data            clears database containing energy data
/clear/jobs            clears database containing job data
/clear/images          clears database containing image file data
```

*IMPORTANT*: The `/reset` must be run to make sure the proper data is in the database.

```
root@bradenp-debug-py-deployment-59b4df4576-lnjpr:/# curl '10.98.23.226:5000/reset'
Data reset 
```

## 'Get` Routes

The following routes can be used to READ data in the database. Data will be returned in a json dictionary format:

```json
"COUNTRY-KEY" : {
    "YEAR" : "VALUE",
    "YEAR" : "VALUE"
    ...
}
```
The `"VALUE"` will be in quad BTU. If the value is "n/a", the database is aware the data does not exist (for example, if the country did not exist in that year). If the value is "null", the value is not in the database. Currently, the only years in the database are 1980 through 2018, but others can be added.

```
/get/all               Gets all data for specified keys (country name, activity type, product type)
/get/date              Gets all data for specified keys for given year
/get/date_range        Gets all data for specified keys for given year range
```

These routes must be queried with at least one of the "ckey params". If a "ckey param" is not queried, all data that matches the other parameters will be returned.

The `get/date` route requires the `year` parameter, and the `get/date_range` requires `year1` and `year2` parameters for the date range. 

Examples:
```
root@bradenp-debug-py-deployment-59b4df4576-lnjpr:/# curl '10.98.23.226:5000/get/all?iso=USA&prodt=NGAS'

# Returns all data for "USA-PROD-NGAS" and "USA-CONS-NGAS" since 'actt' was not specified.
```

```bash
root@bradenp-debug-py-deployment-59b4df4576-lnjpr:/ curl '10.98.23.226:5000/get/date?iso=USA&prodt=NGAS&year=2000'
{
  "USA-CONS-NGAS": {
    "2000": "23.824"
  }, 
  "USA-PROD-NGAS": {
    "2000": "19.662"
  }
}
```

```bash
root@bradenp-debug-py-deployment-59b4df4576-lnjpr:/ curl '10.98.23.226:5000/get/date_range?iso=USA&prodt=NGAS&year1=2000&year2=2003'
{
  "USA-CONS-NGAS": {
    "2000": "23.824", 
    "2001": "22.773", 
    "2002": "23.51", 
    "2003": "22.831"
  }, 
  "USA-PROD-NGAS": {
    "2000": "19.662", 
    "2001": "20.166", 
    "2002": "19.382", 
    "2003": "19.633"
  }
}
```

## 'Delete' Routes

The following routes can be used to DELETE data.

```
/delete/all            Deletes all data for specified keys (country name, activity type, product type)
/delete/date           Deletes all data for specified keys for given year
/delete/date_range     Deletes all data for specified keys for given year range
```

The formatting is identical to the 'Get' Routes. Instead of printing the data, it will be deleted from the database.

## 'Update' Route
The following route can be used to update data. All parameters must be specified. 

```bash
curl '<host ip>:<flask port>/get/date?iso=ISO&actt=ACTT&prodt=PRODT&year=YEAR&value=VALUE'
```
For example, lets say Yugoslavia secretly maintained natural gas production after the dissolution of the USSR:

```bash
# Data = n/a
root@bradenp-debug-py-deployment-59b4df4576-lnjpr:/ curl '10.98.23.226:5000/get/date?iso=YUG&actt=PROD&prodt=NGAS&year=1992'
{
  "YUG-PROD-NGAS": {
    "1992": "n/a"
  }
}

# Update data
root@bradenp-debug-py-deployment-59b4df4576-lnjpr:/ curl '10.98.23.226:5000/update?iso=YUG&actt=PROD&prodt=NGAS&year=1992&value=1.0'
YUG-PROD-NGAS:1992=1.0

# Data = 1.0
root@bradenp-debug-py-deployment-59b4df4576-lnjpr:/ curl '10.98.23.226:5000/get/date?iso=YUG&actt=PROD&prodt=NGAS&year=1992'
{
  "YUG-PROD-NGAS": {
    "1992": "1.0"
  }
}
```

## 'Create' Route

The following route can be used to CREATE a new set of data.
```bash
curl -X POST -H "content-type: application/json" -d '{"country": "ISO-ACTT-PRODT", "data": {"year1": value1, "year2": value2, "yearN": valueN}}' <flask IP>:<flask port>/create
```

For example, let us create a country with ISO `AAA` that consumes solar energy (which is not an energy type in the database yet). The `'ISO-ACTT-PROT'` will be `"AAA-CONS-SOLAR"`.

```bash
root@bradenp-debug-py-deployment-59b4df4576-lnjpr:/ curl -X POST -H "content-type: application/json" -d '{"country": "AAA-CONS-SOLAR", "data": {"2020": 10, "2021": "n/a"}}' 10.98.23.226:5000/create
The following data was created: 
{"AAA-CONS-SOLAR": {"2020": 10, "2021": "n/a"}}

# Verify the data exists
root@bradenp-debug-py-deployment-59b4df4576-lnjpr:/ curl '10.98.23.226:5000/get/all?prodt=SOLAR'
{
  "AAA-CONS-SOLAR": {
    "2020": "10", 
    "2021": "n/a"
  }
}
```

# "Jobs" Routes

The following routes can be used to interact with the "jobs". A "job" entails creating an image for given data.

```
/jobs                  Find data for a specific job
/jobs/all              Prints all jobs and data (No query parameter)
/graph                 Used for instructing worker to create a graph
/get_image             Save an image produced by a job
```

To create a job, POST to  `/graph`.
```bash
curl -X POST -H "content-type: application/json" -d '{"countries": [{"iso": "ISO1", "actt": "ACTT", "prodt": "PRODT"}, {<next country dict>}], "date_range": [YEAR1, YEAR2]}' <flask IP>:<flask port>/graph
```
Like the `/get` and `/delete` routes, if a "ckey param" is not specified, all datasets that match the specified parameters will be selected.

This will return the information about the job, including the jid (job id).

To find the status of the job, use
```bash
 curl '<flask IP>:<flask port>/jobs?jid=<job id>
 ```

 To download the image from cURL:
 ```bash
 curl '<flask IP>:<flask port>/get_image?jid=<job id>' > <filename>.png
 ```
 Note the `>` not used a substitution indicator.

 Alternatively, you can download the image from your browser at the address
 ```
https://isp-proxy.tacc.utexas.edu/bradenp/get_image?jid=<job id>
 ```

 However, this is currently set up to the PROD environment of the k8s pods I am running on ISP02.

###

 For example, say we want to compare the United States' and the World's production of Nuclear Energy:

 ```bash
root@bradenp-debug-py-deployment-59b4df4576-lnjpr:/ curl -X POST -H "content-type: application/json" -d '{"countries": [{"iso": "USA", "actt": "PROD", "prodt": "NUCLEAR"}, {"iso": "WOR","actt": "PROD", "prodt" : "NUCLEAR"}], "date_range": [1980, 1990]}' 10.104.224.168:5000/graph
{
  "countries": "[{\"iso\": \"USA\", \"actt\": \"PROD\", \"prodt\": \"NUCLEAR\"}, {\"iso\": \"WOR\", \"actt\": \"PROD\", \"prodt\": \"NUCLEAR\"}]", 
  "date_range": "[1980, 1990]", 
  "jid": "4f4ce80a-18be-4d7d-a40e-aa9b56f2c0a5", 
  "status": "submitted"
}
root@bradenp-debug-py-deployment-59b4df4576-lnjpr:/ curl '10.104.224.168:5000/jobs?jid=4f4ce80a-18be-4d7d-a40e-aa9b56f2c0a5'
{
  "countries": "[{\"iso\": \"USA\", \"actt\": \"PROD\", \"prodt\": \"NUCLEAR\"}, {\"iso\": \"WOR\", \"actt\": \"PROD\", \"prodt\": \"NUCLEAR\"}]", 
  "date_range": "[1980, 1990]", 
  "image_status": "created", 
  "jid": "4f4ce80a-18be-4d7d-a40e-aa9b56f2c0a5", 
  "status": "complete"
}
root@bradenp-debug-py-deployment-59b4df4576-lnjpr:/ curl '10.104.224.168:5000/get_image?jid=4f4ce80a-18be-4d7d-a40e-aa9b56f2c0a5' > img.png
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 27267  100 27267    0     0  2420k      0 --:--:-- --:--:-- --:--:-- 2662k
```
```bash
[ISP02] $ wget https://isp-proxy.tacc.utexas.edu/bradenp/get_image?jid=03d1dac0-acd2-44b9-8ad2-2ffa98dff915 --no-check-certificate
```

Here is the result:

![alt text][ex1]

[ex1]: https://github.com/bradenpecora/global-energy-data/raw/main/docs/img/example1.png "Example 1"

###

Another example: World production of all product types from 2000 to 2010:

```bash
root@bradenp-debug-py-deployment-59b4df4576-lnjpr:/ curl -X POST -H "content-type: application/json" -d '{"countries": [{"iso": "WOR", "actt": "PROD"}], "date_range": [2000, 2010]}' 10.104.224.168:5000/graph
{
  "countries": "[{\"iso\": \"WOR\", \"actt\": \"PROD\"}]", 
  "date_range": "[2000, 2010]", 
  "jid": "7ab8502f-0109-48cf-8e20-277d9ad62fb6", 
  "status": "submitted"
}
```

Following a similar procedure to get the image, the output is:

![alt text][ex2]

[ex2]: https://github.com/bradenpecora/global-energy-data/raw/main/docs/img/example2.png "Example 2"