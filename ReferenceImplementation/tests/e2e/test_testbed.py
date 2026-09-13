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
from conftest import COMMONS

ROOT = COMMONS.parent
DEPLOY = ROOT / "deploy"
PROFILES = DEPLOY / "profiles"

sys.path.insert(0, str(DEPLOY))
from env import read_profile  # noqa: E402
from testbed import Component, _is_ours, components  # noqa: E402

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
