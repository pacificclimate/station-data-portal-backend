# Configuration

This app is configured primarily with environment variables:

`PCDS_DSN`

- DSN for PCDS/CRMP database.

Optional response caching can be enabled with DragonflyDB or Redis-compatible
storage:

`CACHE_ENABLED`

- Set to `false` to disable response caching intentionally, for example in local
  development. Defaults to `true`.

`CACHE_KEY_PREFIX`

- Prefix used for cache keys. Set this per portal, for example `sdpb-pcds` or
  `sdpb-ynwt`. Defaults to `sdpb`.

`DRAGONFLY_HOST`

- Dragonfly or Redis hostname for metadata response caching.

`DRAGONFLY_PORT`

- Dragonfly or Redis port for metadata response caching. Defaults to `6379`.

`DRAGONFLY_PASSWORD_FILE`

- Optional path to a file containing the Dragonfly or Redis password, such as a
  Docker secret mounted at runtime.

Resource TTLs can be overridden with environment variables. Defaults are shown
below:

- `CACHE_TTL_STATIONS`: `86400` seconds
- `CACHE_TTL_HISTORIES`: `86400` seconds
- `CACHE_TTL_FREQUENCIES`: `604800` seconds
- `CACHE_TTL_NETWORKS`: `604800` seconds
- `CACHE_TTL_VARIABLES`: `604800` seconds

Cache keys use this schema:

```text
<CACHE_KEY_PREFIX>:<resource>:<sha256-of-request-params>
```

Examples:

- `sdpb-pcds:variables:<hash>`
- `sdpb-ynwt:stations:<hash>`
