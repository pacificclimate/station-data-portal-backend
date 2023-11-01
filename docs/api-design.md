# API

## API design

We follow RESTful design principles in this microservice.

We use the very common collection pattern in its RESTful expression. The collection pattern is used when the underlying data can be naturally modelled as a list of individual objects. The list (collection) is a resource, and each individual network is a resource. Each has its own URI. 

For example, in CRMP, the most natural way to regard networks is as a collection of individual networks. It is hard to imagine a better way to represent these items. This is true for the majority of resources provided by this API. 

The API mainly reflects four core tables:

- Network (`/networks`)
- Variable (`/variables`)
- Station (`/stations`)
- History (`/histories`, also included in `/stations` responses)

There are several additional endpoints for more specialized purposes. See the full API design in `sdpb/openapi/api-spec.yaml`.

Following recommended practice for data stores, data in responses is represented in normalized form, which means that any given datum is represented fully only once, and is elsewhere referred to by a unique key.

- For example, each station has a network associated with it. The network is
  referred to by a single key in the station representation.
  Information about the network must be obtained by using the key to
  find the related data from the networks collection.
- Relational keys are the `uri` value for the related object.
  This policy is subject to review. It could be changed to
  `id` to improve "join" speed and (slightly) reduce the size of responses.

In some endpoints, as a convenience, some associated items can be expanded -- that is, a larger amount of information than just the associated item key is provided. 

- For example, the `/stations` endpoint response can include expanded information about associated history records if requested with the `expand` query parameter.
- This is best done only for associated items that are uniquely associated to the main resource. In the case of stations, each history is associated to exactly one station, so each station has a unique collection of histories associated to it. No redundant representations of any single resource (history) are created by expanding such unique items in place. 
- Conversely, it would be a less good idea to expand non-unique items, such as networks, in place.


## Full API

The API is fully defined using [OpenAPI](https://openapis.org/) (formerly known as [Swagger](http://swagger.io/)).

This project's OpenAIP definition is in `sdpb/openapi/api-spec.yaml`.

We use the package [Connexion](https://pypi.org/project/connexion/) to wire up the API definition to code entry points.

Connexion also serves a Swagger UI Console that provides **human-friendly,
interactive documentation** of the API.
It is served at `{base_path}/ui/` where `base_path` is the base path of the API.

