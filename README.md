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
$ git clone https://github.com/pacificclimate/station-data-portal-backend
$ cd station-data-portal-backend
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
export FLASK_APP=sdpb.wsgi
export FLASK_ENV=development
export PCDS_DSN=postgresql://user@host/dbname
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

The API proper is defined using [OpenAPI](https://openapis.org/) 
(formerly known as [Swagger](http://swagger.io/)).

The definition of the SDP backend API is in `sdpb/openapi/api-spec.yaml`.

### Tooling

We use the excellent package [Connexion](https://pypi.org/project/connexion/)
to wire up the API definition to code entry points.
In addition, Connexion serves a Swagger UI Console that provides highly human-friendly, 
interactive documentation of the API. 
It is served at `{base_path}/ui/` where `base_path` is the base path of the API.
