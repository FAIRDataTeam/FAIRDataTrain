"""The testbed's configuration, checked without starting it.

`make up` is what WP-5.5's acceptance criterion needs — "the M1 scenario watched end to end in a
browser" — and a profile that no longer validates is discovered, otherwise, by a person who has
just run it and is now reading a stack trace instead of looking at a screen.

So the profiles are loaded through each component's **own** settings class. That is the point:
a testbed profile is not a separate configuration format, and a station that behaved differently
under `make up` than under its own settings file would be demonstrating the testbed rather than
the station. If a field is renamed in `StationSettings`, this fails here.

What is deliberately *not* checked here is that the components come up — that needs five
processes and a minute, and it is what `make up` itself is for. What is checked is everything
that can be wrong before the first socket is opened: a mistyped key, a port two instances share,
a `base_url` that disagrees with the port it will be served on, a dataset path that does not
exist, and a source list pointing somewhere no component in the testbed is.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import rdflib
from conftest import COMMONS

ROOT = COMMONS.parent
DEPLOY = ROOT / "deploy"
PROFILES = DEPLOY / "profiles"

sys.path.insert(0, str(DEPLOY))
from env import read_profile  # noqa: E402
from testbed import Component, _is_ours, _named, components  # noqa: E402

STATIONS = ("station-ut.env", "station-oosterlicht.env")


def _profile(name: str) -> dict[str, str]:
    values = read_profile(PROFILES / name)
    prefix = str(COMMONS) + "/"
    return {key: value.replace("fdt-commons/", prefix) for key, value in values.items()}


# ------------------------------------------------------------------ they load at all


@pytest.mark.parametrize("name", STATIONS)
def test_a_station_profile_is_valid_station_settings(name: str, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Through `StationSettings`, not a parser of our own: one configuration format."""
    from fdt_station.core.config import StationSettings

    for key, value in _profile(name).items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("FDT_STATION_CONTRACTS_DIR", str(COMMONS))
    settings = StationSettings()          # raises on anything the station would refuse
    assert settings.datasets, "a station with no dataset advertises nothing and serves nothing"
    for dataset in settings.datasets:
        assert dataset.source.exists(), dataset.source


def test_the_registry_profile_is_valid_registry_settings(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    from fdt_registry.core.config import RegistrySettings

    for key, value in _profile("registry.env").items():
        monkeypatch.setenv(key, value)
    settings = RegistrySettings.from_env()
    assert len(settings.sources) == 3


def test_the_depot_profile_is_valid_depot_settings(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    from fdt_depot.core.config import DepotSettings

    for key, value in _profile("depot.env").items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("FDT_COMMONS", str(COMMONS))
    assert DepotSettings.from_env().iri


@pytest.mark.parametrize("name", ["station-ut", "station-oosterlicht"])
def test_a_controller_can_state_a_condition_at_every_station_here(name: str, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """S4 needs both: a credential that says which controller is acting, and somewhere to keep
    what they write.

    Without the second the station answers 501 to every change — honestly, but a testbed whose
    condition builder is read-only demonstrates the read half of a screen whose whole point is
    the write half. And the credential has to name the controller who actually owns data here,
    or the surface authenticates somebody with nothing to say anything about.
    """
    from testbed import _environment

    from fdt_station.core.config import StationSettings

    for key, value in _environment(_named(name)).items():
        monkeypatch.setenv(key, value)
    settings = StationSettings()
    assert settings.conditions_dir is not None, "this station would answer 501 to every change"
    assert settings.conditions_dir.is_absolute()
    assert str(settings.conditions_dir).startswith(str(ROOT / ".testbed"))

    assert settings.controller_tokens, "no controller has standing to state a condition here"
    controllers = {str(c) for c in settings.controller_tokens.values()}
    held = {str(dataset.iri) for dataset in settings.datasets}
    # The station's own reader, not another component's: `hasDataController` for the M1 dataset
    # is in `m1-gene-disease.ttl`, which only the station's corpus loads. Asking a different
    # component's graph would have answered "this controller owns nothing" about a station where
    # they own the only dataset.
    from fdt_station.core.contracts import Contracts as StationContracts

    corpus = StationContracts(COMMONS).catalogue_corpus
    fdt_o = rdflib.Namespace("https://w3id.org/fdt/fdt-o#")
    owners = {
        str(owner)
        for dataset in held
        for owner in corpus.objects(rdflib.URIRef(dataset), fdt_o.hasDataController)
    }
    assert controllers & owners, (
        f"the credential names {controllers}, and the data here belongs to {owners}: this "
        f"station would authenticate a controller with nothing to say anything about"
    )


def test_the_depot_in_this_testbed_can_be_withdrawn_from(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """A store, an operator and a credential, or the testbed's Depot answers 501 to everything.

    Withdrawal is the write operation this testbed can actually show — publishing needs a
    creator's key set, which is deliberately not configured (a Depot resolves creator keys out
    of band and never from the submission, ADR-036). All three of these are needed together: a
    credential with no operator IRI beside it produces a withdrawal by nobody, which is the
    counter-example `invalid/train-withdrawn-by-nobody.ttl` exists to refuse.
    """
    from testbed import _environment

    from fdt_depot.core.config import DepotSettings

    for key, value in _environment(_named("depot")).items():
        monkeypatch.setenv(key, value)
    settings = DepotSettings.from_env()
    assert settings.store_dir is not None, "this Depot would answer 501 to every write"
    assert settings.admin_token and settings.operator
    # resolved to somewhere writable, not left as the repo-relative form the profile carries
    assert settings.store_dir.is_absolute()
    assert str(settings.store_dir).startswith(str(ROOT / ".testbed"))


# ------------------------------------------------------- and they agree with each other


def test_no_two_instances_want_the_same_port() -> None:
    ports = [component.port for component in components(run_plan=True)]
    assert len(set(ports)) == len(ports), ports


def test_each_station_publishes_the_address_it_is_served_on() -> None:
    """`base_url` is what the station puts in its own self-description and what a Handler
    dispatches to. A station served on one port and advertising another is reachable by whoever
    already knows where it is and by nobody who reads its metadata — which is the whole point of
    publishing metadata."""
    for name in STATIONS:
        values = _profile(name)
        assert values["FDT_STATION_BASE_URL"].endswith(f":{values['FDT_TESTBED_PORT']}"), name


def test_the_registry_harvests_the_components_the_testbed_runs() -> None:
    """A source list pointing at nothing is a registry that answers every search with "no
    station matched" — indistinguishable, to a consumer, from a network in which nobody holds
    their data."""
    running = {component.url for component in components(run_plan=True)}
    sources = _profile("registry.env")["FDT_REGISTRY_SOURCES"].split(",")
    assert sources
    for entry in sources:
        kind, _, url = entry.partition("=")
        assert kind in {"station", "depot"}, entry
        assert url in running, f"{url} is not a component this testbed starts"


def test_both_stations_are_in_the_network_the_handler_dispatches_under() -> None:
    """The M1 plan runs under the national research network. A testbed whose station was not in
    it would refuse the plan at negotiation and look like a bug in the station."""
    health_research = "https://example.org/fdt/net/health-research-nl"
    for name in STATIONS:
        networks = {
            membership["network"]
            for membership in json.loads(_profile(name)["FDT_STATION_MEMBERSHIPS"])
        }
        assert health_research in networks, name


def test_the_second_station_is_in_a_network_that_bars_automated_decisions() -> None:
    """Which is the reason it is in the testbed at all.

    With one station the testbed shows the automated path and quietly implies it is the only
    one. The pair is what makes ADR-032 visible: the same request granted by machine in one
    network, and in the other neither granted nor refused by one — evaluated, recommended, and
    put to a person.
    """
    memberships = json.loads(_profile("station-oosterlicht.env")["FDT_STATION_MEMBERSHIPS"])
    barred = [m for m in memberships if m["permits_automated_decision"] is False]
    assert barred, "no network here bars automated decisions; S3 would be an empty queue"
    # and it states the regime rather than leaving it to be assumed (ADR-034, Q19)
    for membership in memberships:
        assert "permits_automated_decision" in membership, membership["network"]


def test_a_station_profile_names_the_credentials_its_consoles_ask_for() -> None:
    """Q21's placeholder, twice over. The operator surface and the controller's queue are two
    different questions asked by two different parties, and each has its own credential
    (ADR-011) — a testbed that configured one would leave half the screens unreadable."""
    assert _profile("station-ut.env")["FDT_STATION_ADMIN_TOKEN"]
    oosterlicht = _profile("station-oosterlicht.env")
    assert oosterlicht["FDT_STATION_ADMIN_TOKEN"]
    assert json.loads(oosterlicht["FDT_STATION_CONTROLLER_TOKENS"])


# ------------------------------------------------------------------------- the reader


def test_a_profile_value_is_taken_verbatim(tmp_path: Path) -> None:
    """The reason `deploy/env.py` exists rather than `set -a; . profile.env`.

    A shell mangles both of the values that matter: `FDT_STATION_DATASETS` is JSON with braces
    and quotes, and `FDT_STATION_TITLE` contains a space and an em dash. The first attempt at
    this failed exactly there, with a JSON decode error three layers down in pydantic.
    """
    profile = tmp_path / "p.env"
    profile.write_text(
        "# a comment\n"
        "\n"
        "TITLE=University station (fictional) — with an em dash\n"
        'JSON=[{"a": 1, "b": "two"}]\n'
        "EMPTY=\n",
        encoding="utf-8",
    )
    values = read_profile(profile)
    assert values["TITLE"] == "University station (fictional) — with an em dash"
    assert json.loads(values["JSON"]) == [{"a": 1, "b": "two"}]
    assert values["EMPTY"] == ""
    assert "# a comment" not in values


def test_a_line_that_is_not_a_setting_is_an_error_and_not_a_shrug(tmp_path: Path) -> None:
    """A profile with a typo must not start a component that is quietly misconfigured."""
    profile = tmp_path / "p.env"
    profile.write_text("FDT_STATION_IRI https://example.org/\n", encoding="utf-8")
    with pytest.raises(ValueError, match="not a KEY=value line"):
        read_profile(profile)


def test_nothing_in_a_value_is_interpreted(tmp_path: Path) -> None:
    """`#` is not a comment inside a value, and quotes are part of the value.

    Both are ordinary `.env` conveniences and both would corrupt a profile here. Every IRI in
    this ecosystem may carry a fragment — `https://w3id.org/fdt/network#StationRole` is in two
    profiles — and truncating at `#` turns it into a different IRI that still parses. Stripping
    quotes turns a JSON string into something that is not JSON, and does it silently.
    """
    profile = tmp_path / "p.env"
    profile.write_text(
        "ROLE=https://w3id.org/fdt/network#StationRole\n"
        'QUOTED="not unwrapped"\n'
        "SPACED=a value with spaces\n",
        encoding="utf-8",
    )
    values = read_profile(profile)
    assert values["ROLE"] == "https://w3id.org/fdt/network#StationRole"
    assert values["QUOTED"] == '"not unwrapped"'
    assert values["SPACED"] == "a value with spaces"


# ----------------------------------------------------------------- is it ours that answered?


def test_a_port_that_answers_is_not_the_same_fact_as_our_component_answering() -> None:
    """The check that was missing on the first run of `make up`.

    It reported a station as healthy on port 8000. There was no station: a Docker container
    somebody had left running answered, and the runner asked only whether *something* did. A
    testbed that reports somebody else's software as up is worse than one that fails, because
    everything after that is measured against the wrong thing.

    Every component publishes its own IRI at `/` — the station as RDF, the others as JSON — so
    the check costs one string search and is not optional.
    """
    station = Component(
        name="station-ut", package="FAIRDataStation-py", port=8400, argv=[],
        identity="https://example.org/fdt/station/ut",
    )

    ours = (
        "<https://example.org/fdt/station/ut> a fdt-o:DataStation ;\n"
        '    dct:title "University station (fictional)" .'
    )
    assert _is_ours(station, ours) is True

    # A FAIR Data Point, which is what was actually on that port. Valid RDF, right shape of
    # answer, entirely the wrong thing.
    somebody_else = (
        "@prefix ns1: <https://w3id.org/fdp/o#> .\n"
        "<http://localhost:8400/> a ns1:MetadataService ."
    )
    assert _is_ours(station, somebody_else) is False

    # And the two ways of not answering at all.
    assert _is_ours(station, None) is False
    assert _is_ours(station, "") is False


def test_every_component_is_checked_against_its_own_configured_identity() -> None:
    """Not merely "has something set".

    An earlier version of this asserted only that the identity looked like a URL, and a mutation
    run walked straight through it by defaulting the field to the string `"http"` — which is in
    every one of these bodies, so the check would have passed for any of them against any of the
    others. The identity has to be the IRI **this instance's profile configures**, which is the
    only string that distinguishes our station from another station on the same port.
    """
    keys = {
        "station-ut": ("station-ut.env", "FDT_STATION_IRI"),
        "station-oosterlicht": ("station-oosterlicht.env", "FDT_STATION_IRI"),
        "depot": ("depot.env", "FDT_DEPOT_IRI"),
        "registry": ("registry.env", "FDT_REGISTRY_IRI"),
    }
    identities = set()
    for component in components(run_plan=True):
        assert component.identity, component.name
        if component.name in keys:
            profile, key = keys[component.name]
            assert component.identity == _profile(profile)[key], component.name
        identities.add(component.identity)
    # and no two components answer to the same one, or the check cannot tell them apart
    assert len(identities) == len(components(run_plan=True))


def test_the_two_stations_do_not_share_an_identity() -> None:
    """The pair is the case the check has to get right: two instances of the same software, on
    adjacent ports, with the same routes. Only the IRI they publish tells them apart."""
    ut = _profile("station-ut.env")["FDT_STATION_IRI"]
    oosterlicht = _profile("station-oosterlicht.env")["FDT_STATION_IRI"]
    assert ut != oosterlicht
    station = Component(name="x", package="p", port=1, argv=[], identity=ut)
    assert _is_ours(station, f"<{ut}> a fdt-o:DataStation .") is True
    assert _is_ours(station, f"<{oosterlicht}> a fdt-o:DataStation .") is False


def test_every_component_admits_the_console_this_testbed_ships_with() -> None:
    """Otherwise `make up` produces six green rows and six consoles that say nothing answered.

    A browser discards a cross-origin response unless the component names the page's origin, so
    a testbed whose components do not name their own console is a testbed that looks perfectly
    healthy from the command line and is unusable from the screen — which is how this was found,
    by a person opening one (Q23).

    The Handler is the one that cannot read a profile, because a Handler has no settings class:
    it is configured by the plan it is given and the arguments it is dispatched with. So the
    runner passes what the others read, from the same profile, and this checks that too.
    """
    consoles = f"http://localhost:{_profile('console.env')['FDT_TESTBED_PORT']}"

    for profile, key in (
        ("station-ut.env", "FDT_STATION_CORS_ORIGINS"),
        ("station-oosterlicht.env", "FDT_STATION_CORS_ORIGINS"),
        ("depot.env", "FDT_DEPOT_CORS_ORIGINS"),
        ("registry.env", "FDT_REGISTRY_CORS_ORIGINS"),
        ("handler.env", "FDT_HANDLER_CORS_ORIGINS"),
    ):
        origins = [o.strip() for o in _profile(profile)[key].split(",")]
        assert consoles in origins, profile

    argv = _named("handler").argv
    passed = [argv[i + 1] for i, item in enumerate(argv) if item == "--allow-origin"]
    assert consoles in passed, "the Handler was told of no console; H3 and H4 would be blank"


# ---------------------------------------------------------------- the testbed's creator identity


def test_the_key_set_the_depot_reads_carries_no_private_material(tmp_path: Path) -> None:
    """Only the public half is ever written, and that is structural rather than careful.

    `write_key_set` builds the document from `public_jwk()`, which derives the public bytes and
    never has the private ones in hand — so there is no path through it that could publish a `d`.
    This asserts the property the structure is there to give, because the structure is one
    refactor away from a function that takes the whole key and drops fields.
    """
    import creator

    path = tmp_path / "creator-keys.json"
    creator.write_key_set(path)
    document = json.loads(path.read_text())

    assert list(document) == [creator.CREATOR]
    keys = document[creator.CREATOR]["keys"]
    assert len(keys) == 1
    assert keys[0]["kty"] == "OKP" and keys[0]["crv"] == "Ed25519"
    for private in ("d", "p", "q", "dp", "dq", "qi", "k", "oth"):
        assert private not in keys[0], f"the Depot's key set carries private material: {private}"


def test_the_derived_key_verifies_what_the_derived_key_signed() -> None:
    """The property that lets the compose have no volume.

    The Depot holds the public half and the seed step signs with the private half, in two
    containers that share no filesystem. They agree only because both derive from the same
    constant — so if that derivation ever stops being deterministic, the symptom is every
    publication refused as a signature that does not verify, with nothing on either side able to
    say why. This is what would fail first instead.
    """
    import creator
    from fdt_depot.signatures import CreatorKeys, DetachedSignature

    digest = "sha256:" + "0" * 64
    signature = creator._private_key().sign(digest.encode())

    keys = CreatorKeys({creator.CREATOR: [creator.public_jwk()]})
    keys.verify(
        DetachedSignature(
            signed_by=creator.CREATOR, key_id=creator.KEY_ID, algorithm="EdDSA",
            signed_digest=digest, value=creator._b64u(signature),
        ),
        expected_digest=digest,
        must_be=creator.CREATOR,
        role="creator",
    )


def test_both_runners_mint_the_depots_key_set() -> None:
    """`make up` and `make up-processes` are two paths and only one of them was exercised.

    A Depot configured with a creator key set and unable to read it refuses to start — which is
    the right behaviour and means a runner that minted on one path alone leaves the other failing
    on a file the first one creates. Found by adding the container path and not the process one.
    """
    source = (DEPLOY / "testbed.py").read_text()
    assert source.count("_mint_creator_keys(") >= 3, (
        "one of the two runners no longer mints the Depot's key set before starting it"
    )


# --------------------------------------------------------------- the agreement signing keys
#
# ADR-038: a station signs the assigner's side of every agreement it concludes, and the Handler
# signs the assignee's with the train owner's key. Three files, and each one is a different
# mistake if it goes wrong.


def test_the_party_keys_a_station_reads_carry_no_private_material(tmp_path: Path) -> None:
    """The one that would be worst, and the one easiest to get wrong by symmetry.

    A station holding the train owner's *private* key could sign in the owner's name, which is
    precisely the arrangement two signatures exist to rule out: the record would carry an
    assignee's signature the assignee never made, verifying perfectly. `write_party_keys` builds
    from `jwk(..., private_half=False)`, and this asserts the property rather than the structure,
    because the structure is one argument away from the other value.
    """
    import agreement_keys

    path = tmp_path / "agreement-party-keys.json"
    agreement_keys.write_party_keys(path)
    document = json.loads(path.read_text())

    assert list(document) == [agreement_keys.OWNER]
    [key] = document[agreement_keys.OWNER]["keys"]
    assert (key["kty"], key["crv"], key["kid"]) == ("OKP", "Ed25519", agreement_keys.OWNER_KEY_ID)
    for private in ("d", "p", "q", "dp", "dq", "qi", "k", "oth"):
        assert private not in key, f"a station's party key set carries private material: {private}"


def test_a_signing_key_set_does_carry_the_private_half(tmp_path: Path) -> None:
    """The other direction, which no other test would notice.

    A key set with only public keys in it is what a party *publishes*, not what it signs with —
    and a station handed one would start, conclude nothing, and report a missing signing key.
    Both halves of `jwk()` matter, so both are asserted.
    """
    import agreement_keys

    path = tmp_path / "station-signing-key.json"
    key_id = agreement_keys.station_key_id("https://example.org/fdt/station/ut")
    agreement_keys.write_signing_key(path, key_id)

    [key] = json.loads(path.read_text())["keys"]
    assert key["kid"] == key_id
    assert key["d"] and key["x"], "a signing key set without a private half signs nothing"


def test_the_two_sides_keys_are_different_keys() -> None:
    """Derived per key id, not one key wearing two names.

    One key shared between the station and the train owner would make both signatures verify
    against the same public half — and an agreement whose two signatures are one party's is
    exactly what the roles and the party binding exist to detect. It would pass every other test
    here, because every other test only asks whether the signatures verify.
    """
    import agreement_keys

    station = agreement_keys.jwk(
        agreement_keys.station_key_id("https://example.org/fdt/station/ut"), private_half=True)
    owner = agreement_keys.jwk(agreement_keys.OWNER_KEY_ID, private_half=True)
    assert station["x"] != owner["x"]
    assert station["d"] != owner["d"]


def test_the_derived_agreement_key_verifies_what_it_signed() -> None:
    """The property that lets the compose have no volume, for the agreement keys this time.

    The station container holds the owner's public half and the Handler container signs with the
    private half; they share no filesystem and agree only because both derive from one constant.
    If that stops being deterministic the symptom is every visit stopping at
    `negotiation.awaiting-signature` with the station reporting a signature that does not verify —
    and nothing on either side able to say why. This is what would fail first instead.
    """
    import base64

    import agreement_keys
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    digest = "sha256:" + "0" * 64
    signature = agreement_keys._private_key(agreement_keys.OWNER_KEY_ID).sign(digest.encode())

    published = agreement_keys.jwk(agreement_keys.OWNER_KEY_ID, private_half=False)
    raw = base64.urlsafe_b64decode(published["x"] + "=" * (-len(published["x"]) % 4))
    Ed25519PublicKey.from_public_bytes(raw).verify(signature, digest.encode())


def test_both_runners_mint_the_agreement_keys() -> None:
    """The same two paths as the Depot's creator key, and the same way of getting it wrong.

    A station configured with a signing key and without one does not fail loudly at a file it
    cannot read — it starts, concludes nothing, and every visit rests at
    `negotiation.requested`. The testbed would come up with every console screen downstream of a
    run empty, which reads as a broken console rather than a missing file.
    """
    source = (DEPLOY / "testbed.py").read_text()
    assert source.count("_mint_agreement_keys(") >= 3, (
        "one of the two runners no longer mints the agreement signing keys before starting"
    )


def test_every_station_profile_that_negotiates_has_a_signing_key() -> None:
    """A station with no key concludes nothing (ADR-038), so a profile without one is a station
    that would come up and never agree to anything — which is the testbed with its point removed.
    """
    for profile in sorted(PROFILES.glob("station-*.env")):
        values = read_profile(profile)
        assert values.get("FDT_STATION_SIGNING_KEY"), f"{profile.name} signs no agreement"
        assert values.get("FDT_STATION_PARTY_KEYS"), (
            f"{profile.name} could not check an assignee's signature and would refuse every one "
            f"as a key it was never told about"
        )
