# Station Data Portal Backend

The Station Data Portal Backend is a (meta)data microservice for the
[Station Data Portal](https://github.com/pacificclimate/station-data-portal) 
app.

At present, this service provides only metadata. Actual data downloads
are provided by an instance of the PDP backend.

## Summary

This service provides data serving the needs of Station Data Portal and
similar apps.

## Installation

It is best practice to install using a virtual environment.
We use [`pipenv`](https://pipenv.pypa.io/en/latest/) 
to manage dependencies and create a virtual environment.

To clone the project:

```bash
$ git clone https://github.com/pacificclimate/station-data-portal-backend
```

To install the project:

```bash
$ cd station-data-portal-backend
$ pipenv install
```

## Run the service

To run a dev server locally:

```bash
export PCDS_DSN=postgresql://user@host/dbname
export FLASK_APP=sdpb.wsgi
export FLASK_ENV=development
pipenv run flask run
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

We use the package [Connexion](https://pypi.org/project/connexion/)
to wire up the API definition to code entry points.
Connexion also serves a Swagger UI Console that provides human-friendly, 
interactive documentation of the API. 
It is served at `{base_path}/ui/` where `base_path` is the base path of the API.
