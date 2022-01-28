# API

## API design

We follow RESTful design principles in this microservice.

We us the very common collection pattern in its
RESTful expression, e.g., for the `/stations` endpoint.

Overall design of API mainly reflects four core tables:

* Network (`/networks`)
* Variable (`/variables`)
* Station (`/stations`)
* History (`/histories`, also included in `/stations` responses)

Following recommended practice for data stores (see, e.g., Redux),
data is represented in normalized form.

* For example, a station has a network associated with it. The network is
  referred to by a single key in the station representation.
  Information about the network must be obtained by using the key to
  find the related data from the networks collection.

* Relational keys are the `uri` value for the related object.
  This policy is subject to review. It could be changed to
  `id` to improve "join" speed.


## Full API

The API is fully defined using [OpenAPI](https://openapis.org/)
(formerly known as [Swagger](http://swagger.io/)).

The definition in `sdpb/openapi/api-spec.yaml`.

We use the package [Connexion](https://pypi.org/project/connexion/)
to wire up the API definition to code entry points.

Connexion also serves a Swagger UI Console that provides **human-friendly,
interactive documentation** of the API.
It is served at `{base_path}/ui/` where `base_path` is the base path of the API.

