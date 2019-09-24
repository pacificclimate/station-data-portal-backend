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
export FLASK_APP=sdpb.wsgi
export FLASK_ENV=development
flask run
```


## API design

We follow RESTful design principles in this microservice.

Specifically, we will be using the very common collection pattern in its
RESTful expression, e.g., for the `/stations` endpoint.

#### Metadata endponts

Overall design of API mainly reflects four core tables:

* Network (`/networks`)
* Variable (`/variables`)
* Station (`/stations`)
* History (part of `/stations`, also available but not used at `/histories`)

Following recommended practice for data stores (see, e.g., Redux), 
data is represented in normalized form. 

* For example, a station has a network associated with it. The network is
referred to by a single key in the station representation. 
Information about the network must be obtained by using the key to 
find the related data from the networks collection.

* Relational keys are the `uri` value for the related object.
This policy is subject to review. In fact, it should be changed to
`id` if only to improve efficiency.

#### Data endpoints (provisional)

**Note**: We have not settled on (a) building and using a new data endpoint(s), 
nor (b) if we do, whether the new endpoint will accept a list of stations (station ids).
However, this discussion assumes both those things. 

Data is provided through the following endpoints:

* Climatologies (`/observations/climatologies.{format}`)
* Timeseries (`/observations/timeseries.{format}`)

The UI enables the user to select an arbitrary set of stations and request data for them.

Because the user can select any number of stations (presently there are over 7000 stations in the CRMP database), 
the parameters to the data endpoints can be very large in number. 

##### RESTful GET with large parameter sets: The great debate

For data-retrieval endpoints (of which these are an example), RESTful API design guidelines 
clearly indicate that the HTTP verb to use is `GET`.

`GET` normally passes the parameters defining what is retrieved in the query string.
In pre-2014 versions of the HTTP standard, the body of a `GET` request was to have no effect on
its semantics (i.e., cannot affect its results). A more recent version states removes that limitation,
but many servers will drop the body, ignore the request, or otherwise **** up your `GET` if you send
it with a body. And you will almost certainly lose caching, which in the vast majority of servers
is predicated on the request URL only, and not on the body.

But what if your parameter set is large enough to exceed the common request length limitations 
of between 2k and 8k octets? Then you will be tempted to send your arbitrarily long parameter set
in the request body of the `GET`, which is now not officially discouraged, but might be rejected or 
messed up by half the servers in the world. And you will probably lose effective caching.

Here are a few useful articles on this problem:

* [HTTP GET with request body (SO)](https://stackoverflow.com/questions/978061/http-get-with-request-body)
* [Best practice for REST API call with many parameters (SO)](https://softwareengineering.stackexchange.com/questions/377739/best-practice-for-rest-api-call-with-many-parameters)
* [Limitations of the GET method in HTTP (Dropbox developers' blog)](https://blogs.dropbox.com/developers/2015/03/limitations-of-the-get-method-in-http/)
* [Empty Search (Elasticsearch)](https://www.elastic.co/guide/en/elasticsearch/guide/current/_empty_search.html)

The upshot of all these articles is that, shedding tears, we must abandon the technically perfect
"`GET` with body" approach for the pragmatic substitution of the `POST` verb for `GET`. But we lose
caching. Which in our case may not matter, as the exact same download is unlikely to be called
for repeatedly.

A more pure RESTful approach treats the requests as well as the results as resources, 
but it is significantly more complex:

1. `POST` to the endpoint, e.g., `/observations/timeseries.csv`, specifying parameters in request
body.
   * Creates a new resource
   * Identity of new resource is communicated through the usual header field.
   * Resource identifier would probably best be a hash of the request params
     and the current datetime (because request results will differ depending on when they
     are made). E.g., `/observations/timeseries.csv/foobarbazquz037653434`.
   * Under the hood, the new resource is stored just as the parameters.
2. `GET` to the returned resource endpoint.
   * Parameters are retrieved and used to construct actual content of the response,
     which is the data specified by the response.
3. Here's a trick: The response to a `POST` request **may** include, as a response body, 
a representation of
the newly created resource. Which means you can skip the `GET` above, but you do that at the cost
of loss of cacheability and safety etc. if your client app just keeps issuing `POSTS` on retry. 
Depends on how you feel about adding 300 ms to a download that might take several minutes.
    



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
