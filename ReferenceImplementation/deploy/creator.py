"""The testbed's train creator: an identity that exists only here, and publishes one train.

WP-5.5's acceptance criterion has two halves. The first — the M1 scenario watched end to end —
the testbed has always been able to show. The second is *a train published to the Depot and found
through the registry by its data requirement*, and it could not be shown at all: WP-5.2b built the
Depot's write surface and nothing ever configured the testbed to use it, so `FDT_DEPOT_CREATOR_KEYS`
stayed commented out and every submission was refused as an unknown key. This is that
configuration.

**The key is derived, not stored, and that is what lets there be no volume.** The compose shares
no filesystem between services on purpose (`deploy/compose.yaml`), so the Depot — which must hold
the creator's *public* key before it starts — and the seed step — which must hold the *private*
half to sign with — have no way to pass one to the other. They do not need one: both derive the
same Ed25519 key from a constant below, independently, in their own containers.

**This is a testbed trick and must never be read as a pattern.** A signing key derived from a
constant in a public repository is a key everybody has. It is right here for the same reason
`FDT_DEPOT_ADMIN_TOKEN=fdt-testbed-depot-operator` is right here — nothing in this testbed is a
secret and nothing in it is real — and it is wrong everywhere else. A real creator generates a key
they keep, and gives the Depot the public half out of band; that is what `CreatorKeys` is written
for and nothing about it changes.
"""

from __future__ import annotations

import base64
import hashlib
import json
import pathlib
import urllib.error
import urllib.request
from typing import Any

#: The creator `examples/train-withdrawn.ttl` names as `dct:creator` of the train below. The
#: testbed publishes that train, so it must sign as that party: a signature by anybody else is
#: valid cryptography and an attempt to publish in another party's name, which the Depot refuses
#: as `NotTheCreator` and which is the more interesting of its two refusals.
CREATOR = "https://example.org/fdt/party/open-genomics-collective"
KEY_ID = "https://example.org/fdt/party/open-genomics-collective#testbed"

#: 32 bytes, derived so the constant is readable and the seed is not a row of hex nobody can
#: check. Deterministic on purpose — see the module docstring.
_SEED = hashlib.sha256(b"fdt-testbed-creator-key-not-a-secret-v1").digest()

#: The train the testbed publishes. `examples/train-withdrawn.ttl` describes it *after* its
#: creator withdrew it; what is published here is what they submitted, so the withdrawal is left
#: off. Using a real fixture rather than inventing one matters for the reason the seeded visit
#: gives: a testbed that made up a train would be demonstrating the train.
TRAIN = "https://example.org/fdt/train/variant-burden"
FIXTURE = "examples/train-withdrawn.ttl"
PAYLOAD = "examples/payloads/gene-disease-1.3.rq"
PAYLOAD_MEDIA_TYPE = "application/sparql-query"


def _private_key() -> Any:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    return Ed25519PrivateKey.from_private_bytes(_SEED)


def _b64u(raw: bytes) -> str:
    """base64url, unpadded — what a JWK's `x` and `fdt-p:signatureValue` are."""
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _b64(raw: bytes) -> str:
    """Standard base64, padded — what `PayloadBytes.bytes` is.

    Not the same encoding as the one above, and the Depot is strict about both: the payload is
    decoded with `validate=True`, so base64url slips through only when the bytes happen to
    contain no character the two alphabets disagree on. A publisher that used one encoding
    throughout would work until the first payload with a `+` or a `/` in its encoding, and would
    then fail as a digest mismatch — which reads as tampering rather than as a client bug.
    """
    return base64.b64encode(raw).decode()


def public_jwk() -> dict[str, Any]:
    from cryptography.hazmat.primitives import serialization

    raw = _private_key().public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return {"kty": "OKP", "crv": "Ed25519", "x": _b64u(raw), "kid": KEY_ID, "alg": "EdDSA"}


def write_key_set(path: pathlib.Path) -> None:
    """What the Depot reads at startup: creator IRI → the keys it will accept.

    Only the public half is ever written. There is no code path here that could write a private
    key into the Depot's configuration, because the function that builds the document never has
    one — the same property `fdt_depot.keys.public_jwks` is written for, one layer out.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({CREATOR: {"keys": [public_jwk()]}}, indent=2))


def _submission(commons: pathlib.Path) -> tuple[str, bytes]:
    """The train as its creator submitted it, and the payload bytes it declares.

    The withdrawal is removed from the graph rather than from the text. Editing Turtle with string
    replacement produces a document that may not parse, and a test or a testbed that then reports
    a failure is reporting on its own edit.
    """
    import rdflib

    graph = rdflib.Graph()
    graph.parse(commons / FIXTURE, format="turtle")

    prov = rdflib.Namespace("http://www.w3.org/ns/prov#")
    train = rdflib.URIRef(TRAIN)
    for withdrawal in list(graph.objects(train, prov.wasInvalidatedBy)):
        graph.remove((train, prov.wasInvalidatedBy, withdrawal))
        for triple in list(graph.triples((withdrawal, None, None))):
            graph.remove(triple)

    return graph.serialize(format="turtle"), (commons / PAYLOAD).read_bytes()


def publish(depot_url: str, commons: pathlib.Path, *, timeout: float = 30.0) -> str:
    """Publish the train, signed. Returns a line saying what happened, for the runner to print.

    Never raises. A testbed whose Depot would not take a publication is a testbed with one screen
    less on it, not a testbed that failed to come up — and the reason is worth printing, because
    every one of the Depot's refusals names a different thing to go and fix.
    """
    import rdflib

    from fdt_depot.canonical import submission_digest

    try:
        description, payload = _submission(commons)
        graph = rdflib.Graph()
        graph.parse(data=description, format="turtle")
        digest = submission_digest(graph, payload)

        signature = _private_key().sign(digest.encode())
        body = json.dumps({
            "description": description,
            "descriptionMediaType": "text/turtle",
            "payload": {"mediaType": PAYLOAD_MEDIA_TYPE, "bytes": _b64(payload)},
            "signature": {
                "signedBy": CREATOR,
                "keyId": KEY_ID,
                "algorithm": "EdDSA",
                "signedDigest": digest,
                "value": _b64u(signature),
            },
        }).encode()

        request = urllib.request.Request(
            f"{depot_url.rstrip('/')}/trains", data=body, method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=timeout) as answer:  # noqa: S310
            published = json.loads(answer.read())
        return f"published train  {published.get('iri', TRAIN)} — signed by its creator"
    except urllib.error.HTTPError as refused:
        detail = refused.read().decode(errors="replace")[:300]
        if refused.code == 409:
            return f"train already published  {TRAIN}"
        return f"PUBLICATION REFUSED ({refused.code}): {detail}"
    except Exception as failed:                                   # noqa: BLE001 — see docstring
        return f"PUBLICATION DID NOT RUN: {type(failed).__name__}: {failed}"
