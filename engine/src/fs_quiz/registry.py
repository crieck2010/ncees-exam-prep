"""Generator registry: domain -> topic -> generator function.

Generators are plain functions ``fn(rng, qid) -> Question`` registered with the
``@register`` decorator. The registry is the single discovery point for the
engine, CLI, tests, and docs — add a domain by writing one module and
importing it (see docs/ADDING_A_DOMAIN.md).
"""
from __future__ import annotations

_REGISTRY: dict = {}


def register(domain: str, topic: str):
    """Decorate a generator ``fn(rng) -> Question`` for a domain/topic."""
    def deco(fn):
        _REGISTRY.setdefault(domain, {})[topic] = fn
        fn._fs_domain = domain
        fn._fs_topic = topic
        return fn
    return deco


def list_domains() -> list:
    return sorted(_REGISTRY)


def list_topics(domain: str) -> list:
    return sorted(_REGISTRY.get(domain, {}))


def get_generator(domain: str, topic: str):
    try:
        return _REGISTRY[domain][topic]
    except KeyError:
        raise KeyError(f"no generator for domain={domain!r} topic={topic!r}")


def registry_snapshot() -> dict:
    """{domain: [topics]} — used by docs generation and the Flutter contract."""
    return {d: list_topics(d) for d in list_domains()}
