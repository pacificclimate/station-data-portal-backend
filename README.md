# Station Data Portal Backend

Data service for [Station Data Portal](https://github.com/pacificclimate/station-data-portal) app.

## Summary

This microservice provides data serving the needs of Station Data Portal and
similar apps.

## Installation

It is best practice to install using a virtual environment.
Current recommended practice for Python3.3+ to use the [builtin `venv` module](https://docs.python.org/3/library/venv.html).
(Alternatively, `virtualenv` can still be used but it has shortcomings corrected in `venv`.)
See [Creating Virtual Environments](https://packaging.python.org/installing/#creating-virtual-environments) for an
overview of these tools.

```bash
$ git clone https://github.com/pacificclimate/weather-anomaly-data-service
$ cd weather-anomaly-data-service
$ python3 -m venv venv
$ source venv/bin/activate
(venv)$ pip install -U pip
(venv)$ pip install -i https://pypi.pacificclimate.org/simple/ -e .
(venv)$ pip install -r test_requirements.txt
```

## Run the service

To run a dev server locally:

```bash
source venv/bin/activate
export FLASK_APP=sdpb:flask_app
export FLASK_ENV=development
flask run
```


## API design

We follow RESTful design principles in this microservice.

Specifically, we will be using the very common collection pattern in its
RESTful expression, e.g., for the `/stations` endpoint.

Overall design of API mainly reflects four core tables:

* Network (`/networks`)
* Variable (`/variables`)
* Station (`/stations`)
* History (part of `/stations`)

Following recommended practice for data stores (see, e.g., Redux), 
data is represented in normalized form. 

* For example, a station has a network associated with it. The network is
referred to by a single key in the station representation. 
Information about the network must be obtained by using the key to 
find the related data from the networks collection.

* Relational keys are the `uri` value for the related object.
This policy is subject to review. In fact, it should be changed to
`id` if only to improve efficiency.


## API

This is a **sketch only**. 
It should be migrated to and filled out in a Swagger definition.
Do not add a lot of detail here.

### Networks

**`GET /networks`**

List of all networks

Response:

```javascript
[
  {
    "id": String,  // This is not strictly necessary, as uri serves as a unique identifier
    "uri": String, // '/networks/{id}'
    "name": String,
    "long_name": String,
    "virtual": String,  // what does this mean??
    "color": String,  // needed?
  }
]
```

**`GET /networks/{id}`**

Individual network

```javascript
{
 // same as `/networks` list item
}
```

### Variables

**`GET /variables`**

List of all variables collected in database. 

Response:

```javascript
[
  {
    "id": String,  // This is not strictly necessary, as uri serves as a unique identifier
    "uri": String, // '/variables/{id}'
    "name": String,  // aka net_var_name
    "display_name": String,
    "short_name": String,
    "standard_name": String,
    "cell_method": String,
    "unit": String,
    "precision": Number,
    "network_uri": String // '/networks/{id}'
  }
]
```

**`GET /variables/{id}`**

Individual variable description. 

May include additional information.

Response:

```javascript
{
 // same as `/variables` list item?
}
```

### Stations

**`GET /stations`**

List of all stations.

Includes enough data to display it on the map and perform necessary filtering.


Response:

```javascript
[
  {
    "id": String,
    "uri": String,
    "native_id": String,
    "min_obs_time": String,
    "max_obs_time": String,
    "network_uri": String,  // unique identifier
    // histories should be sorted by sdate/edate
    // history[0] will, at least initially, be the supplier of all this info;
    // others will be there for some unspecified future application
    "histories": [  
      {
        "id": String,
        "station_name": String,
        "lon": Number,
        "lat": Number,
        "elevation": Number,
        "sdate": String,
        "edate": String,
        "tz_offset": String,  // or omit, and insist sdate, edate are UTC
        "province": String,
        "country": String,
        "freq": String,
        // Variables collected during this history, as follows: 
        // { variable | history -> observation -> variable }
        "variable_uris": [
            String, // '/variables/{id}'; unique identifier
        ]
      }
    ],
  }
]
```

**`GET /stations/{id}`**

Individual station description. 

May include additional information.

Response:

```javascript
{
 // same as `/stations` list item
}
```
