"""The testbed's agreement signing keys, derived rather than stored — ADR-038.

An agreement carries a signature from each party. A station signs the assigner's side and needs
a key of its own; a Handler signs the assignee's side with the train owner's key; and the station
has to hold the owner's *public* key before it starts, or it refuses every signature as one it
was never told about.

**Derived, for the same reason `deploy/creator.py` is derived.** The compose shares no filesystem
between services on purpose, so the station container and the Handler container have no way to
pass a key to each other. They do not need one: each derives the same Ed25519 key from a constant
below, in its own container, and only the public half is ever written into a station's
configuration.

**This is a testbed trick and must never be read as a pattern.** A signing key derived from a
constant in a public repository is a key everybody has. In a deployment each party generates a
key they keep and publishes the public half — that is what `SigningKey`, `PartyKeys` and
`OwnerKey` are written for, and nothing about them changes here.
"""

from __future__ import annotations

import base64
import hashlib
import json
import pathlib
from typing import Any

#: The train owner the testbed's Handler acts for — the party the M1 request names as assignee,
#: and therefore the party whose signature the stations must be able to check.
OWNER = "https://example.org/fdt/party/eu-cardionet-like"
OWNER_KEY_ID = "https://handler.cardionet.example/fdt/v1/keys/1"

_SEED_PREFIX = b"fdt-testbed-agreement-key-not-a-secret-v1|"


def _private_key(key_id: str) -> Any:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    return Ed25519PrivateKey.from_private_bytes(
        hashlib.sha256(_SEED_PREFIX + key_id.encode()).digest()
    )


def _b64u(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _raw_public(private: Any) -> bytes:
    from cryptography.hazmat.primitives import serialization

    return bytes(private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw))


def _raw_private(private: Any) -> bytes:
    from cryptography.hazmat.primitives import serialization

    return bytes(private.private_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()))


def jwk(key_id: str, *, private_half: bool) -> dict[str, Any]:
    private = _private_key(key_id)
    key: dict[str, Any] = {"kty": "OKP", "crv": "Ed25519", "alg": "EdDSA", "use": "sig",
                           "kid": key_id, "x": _b64u(_raw_public(private))}
    if private_half:
        key["d"] = _b64u(_raw_private(private))
    return key


def station_key_id(station_iri: str) -> str:
    return f"{station_iri.rstrip('/')}#agreement-signing"


def write_signing_key(path: pathlib.Path, key_id: str) -> None:
    """A JWK Set with the private half — what a station or a Handler signs with."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"keys": [jwk(key_id, private_half=True)]}, indent=2))


def write_party_keys(path: pathlib.Path) -> None:
    """Party IRI → the PUBLIC keys a station will accept an assignee's signature from.

    Only the public half, and that is the property worth keeping: a station holding the train
    owner's private key could sign in the owner's name, which is precisely the arrangement two
    signatures exist to rule out.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(
        {OWNER: {"keys": [jwk(OWNER_KEY_ID, private_half=False)]}}, indent=2))
