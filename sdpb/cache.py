import hashlib
import json
import logging
import os

import redis

logger = logging.getLogger("sdpb")


DEFAULT_CACHE_TTLS = {
    "stations": 86400,  # 1d
    "histories": 86400,  # 1d
    "frequencies": 604800,  # 1wk
    "networks": 604800,  # 1wk
    "variables": 604800,  # 1wk
}

_cache_client = None
_cache_disabled = False


def _read_password_file(path):
    if not path:
        return None

    with open(path) as fp:
        return fp.read().strip()


def _truthy(value):
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def cache_enabled():
    return _truthy(os.getenv("CACHE_ENABLED", "true"))


def cache_ttl(namespace):
    env_var = f"CACHE_TTL_{namespace.upper()}"
    return int(os.getenv(env_var, DEFAULT_CACHE_TTLS[namespace]))


def get_cache_client():
    global _cache_client, _cache_disabled

    if _cache_client is not None:
        return _cache_client
    if _cache_disabled:
        return None
    if not cache_enabled():
        _cache_disabled = True
        return None

    host = os.getenv("DRAGONFLY_HOST")
    port = int(os.getenv("DRAGONFLY_PORT", 6379))
    password_file = os.getenv("DRAGONFLY_PASSWORD_FILE")

    if not host:
        _cache_disabled = True
        return None

    try:
        _cache_client = redis.Redis(
            host=host,
            port=port,
            password=_read_password_file(password_file),
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )
        _cache_client.ping()
        return _cache_client
    except Exception:
        logger.exception("Failed to initialize response cache")
        _cache_disabled = True
        return None


def cache_get_or_set(namespace, params, producer):
    client = get_cache_client()
    ttl = cache_ttl(namespace)
    if client is None:
        return producer()

    digest = hashlib.sha256(
        json.dumps(params, sort_keys=True, separators=(",", ":"), default=str).encode(
            "utf-8"
        )
    ).hexdigest()
    key = f"sdpb:{namespace}:{digest}"

    try:
        cached_value = client.get(key)
        if cached_value is not None:
            return json.loads(cached_value)
    except Exception:
        logger.exception("Failed to read from response cache for %s", namespace)

    result = producer()

    try:
        client.setex(
            key,
            ttl,
            json.dumps(result, sort_keys=True, separators=(",", ":"), default=str),
        )
    except Exception:
        logger.exception("Failed to write to response cache for %s", namespace)

    return result
