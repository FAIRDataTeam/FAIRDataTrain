"""The compose and the runner describe the same testbed.

`make up` runs the ecosystem as containers and `make up-processes` runs it as processes out of
the checkout. Both are the same description — `deploy/testbed.py`'s `components()` — because the
compose services do not repeat a port, an argument or an identity in YAML: each one runs
`testbed.py exec <name>` and is health-checked with `testbed.py health <name>`.

That is an arrangement, not a guarantee, and this file is what makes it one. Nothing here starts
a container: what is checked is everything that can be wrong before the first image is pulled —
a service that runs a component the runner does not know, a published port that no profile
configures, a station image built from the Depot's source, a port published on every interface
of the machine rather than on the loopback address.

The one test that does need Docker asks it to parse a profile and compares the answer with
`deploy/env.py`'s, because two parsers reading one file is the arrangement's only real risk.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from conftest import COMMONS

ROOT = COMMONS.parent
DEPLOY = ROOT / "deploy"
PROFILES = DEPLOY / "profiles"
COMPOSE = DEPLOY / "compose.yaml"
FRONT_DOOR = DEPLOY / "docker" / "console-index.html"

sys.path.insert(0, str(DEPLOY))
from env import read_profile  # noqa: E402
from testbed import _named, components, health  # noqa: E402

#: The namespace owner, and the only service that may publish a port.
NET = "net"


def _compose() -> dict[str, dict]:  # type: ignore[type-arg]
    return yaml.safe_load(COMPOSE.read_text(encoding="utf-8"))


def _services() -> dict[str, dict]:  # type: ignore[type-arg]
    return _compose()["services"]


def _exec_name(service: dict) -> str | None:  # type: ignore[type-arg]
    """The component a service becomes, if it becomes one: `… exec <name> …`."""
    command = service.get("command") or []
    return command[command.index("exec") + 1] if "exec" in command else None


def _component_services() -> dict[str, dict]:  # type: ignore[type-arg]
    return {name: s for name, s in _services().items() if _exec_name(s) is not None}


# --------------------------------------------------------------- one testbed, two ways to run it


def test_the_compose_runs_exactly_the_components_the_runner_knows() -> None:
    """A service the runner does not know would start and then be absent from `make status`,
    which is the one place a person looks to find out whether the testbed is up."""
    in_compose = {_exec_name(s) for s in _component_services().values()}
    assert in_compose == {component.name for component in components(run_plan=True)}


def test_a_service_becomes_the_component_its_own_name_says() -> None:
    """`station-ut`'s container must not be Oosterlicht's.

    The two are the same image and differ only in which profile they are given, so a name
    crossed here would produce a testbed that looks entirely normal — two stations, two ports —
    and shows the same station twice.
    """
    for service, definition in _component_services().items():
        assert _exec_name(definition) == service, service


def test_each_image_is_built_from_the_component_it_serves() -> None:
    """`COMPONENT` is the submodule that gets installed. A station image built from `TrainDepot`
    would fail at start-up; one built from the Handler would *succeed* and answer the station's
    routes with 404."""
    packages = {component.name: component.package for component in components(run_plan=True)}
    for service, definition in _component_services().items():
        args = definition["build"]["args"]
        assert args["COMPONENT"] == packages[service], service


def test_the_two_stations_are_one_image_and_two_profiles() -> None:
    """Which is the whole claim the pair makes: the difference between a station that decides by
    machine and one that may not is configuration, not software (ADR-034)."""
    services = _services()
    ut, oosterlicht = services["station-ut"], services["station-oosterlicht"]
    assert ut["image"] == oosterlicht["image"]
    assert ut["env_file"] != oosterlicht["env_file"]


def test_each_service_is_given_the_profile_of_the_instance_it_is() -> None:
    profiles = {
        component.name: component.profile or "handler.env"
        for component in components(run_plan=True)
    }
    profiles["consoles"] = "console.env"
    for service, expected in profiles.items():
        given = _services()[service]["env_file"]
        assert [Path(entry).name for entry in given] == [expected], service


# --------------------------------------------------------------------- one address space


def test_every_service_shares_the_one_network_namespace() -> None:
    """`localhost:8400` inside a container is `localhost:8400` on the host, and that is what
    makes the addresses these components publish about themselves true.

    A registry indexes where a station and a Depot are, and a console follows what it indexed —
    H1 resolves a train by fetching the Depot URL the registry recorded, from a browser, on the
    host. Under ordinary compose networking the registry would harvest `http://depot:8402`,
    which no browser can reach, and the index would be full of addresses that work in one place
    only.
    """
    for service, definition in _services().items():
        if service == NET:
            continue
        assert definition.get("network_mode") == f"service:{NET}", service


def test_only_the_namespace_owner_publishes_a_port() -> None:
    """Docker refuses `ports:` on a service that shares another's network stack, so this is not
    style: a port added to a component service would not be a misconfiguration to find later, it
    would stop the testbed from coming up at all."""
    for service, definition in _services().items():
        if service == NET:
            continue
        assert "ports" not in definition, service


def _published() -> list[tuple[str, int, int]]:
    rows = []
    for entry in _services()[NET]["ports"]:
        address, host_port, container_port = str(entry).rsplit(":", 2)
        rows.append((address, int(host_port), int(container_port)))
    return rows


def test_the_published_ports_are_the_ports_the_profiles_configure() -> None:
    """The one place in the compose where a number is written, and therefore the one place it
    can disagree with a profile. A component served on a port nobody published is a component
    that is running and unreachable, which reads on screen as a component that is down."""
    configured = {component.port for component in components(run_plan=True)}
    configured.add(int(read_profile(PROFILES / "console.env")["FDT_TESTBED_PORT"]))
    assert {host for _, host, _ in _published()} == configured


def test_a_published_port_is_the_same_port_inside_and_out() -> None:
    """Remapping would break the shared address space quietly: a station would publish the
    address it was reachable at from inside the testbed and not the one a browser uses."""
    for address, host_port, container_port in _published():
        assert host_port == container_port, address


def test_the_testbed_is_published_to_this_machine_and_no_further() -> None:
    """The stations are configured with `FDT_STATION_AUTH_REQUIRED=false`.

    That is a deliberate act of configuration for a testbed — a station that accepted anonymous
    visits by accident could not say who ran a train against its data — and it is also a door
    that must not open onto a café's wifi. Every port is bound to the loopback address.
    """
    for address, host_port, _ in _published():
        assert address == "127.0.0.1", f"{host_port} is published on {address}"


def test_a_container_binds_more_than_its_own_loopback() -> None:
    """The bug this caught, which every health check in the testbed reported as healthy.

    `exec` took `--host`, passed it to nothing, and `components()` used its default: each
    component bound 127.0.0.1 *inside its own network namespace*. The container's health check
    asks 127.0.0.1 from inside that same namespace, so all five were healthy and nothing on the
    host could reach any of them. A container can always talk to itself; only a question asked
    from outside can tell the difference, which is why `make up` ends by asking one.
    """
    for service, definition in _component_services().items():
        command = definition["command"]
        assert command[command.index("--host") + 1] == "0.0.0.0", service

    for component in components(run_plan=True):
        argv = _named(component.name, host="0.0.0.0").argv
        assert argv[argv.index("--host") + 1] == "0.0.0.0", component.name


def test_exec_binds_the_address_it_was_told_to(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """And the test above did not say that.

    It checked that `components()` and `_named()` can produce `--host 0.0.0.0`, which they
    always could. The defect was one line further on: `exec` took the address, looked it up in a
    component list built with the default, and handed uvicorn the loopback. A mutation run put
    that line back and walked straight through the check above — so this asks the command
    itself, at the last point before the process is replaced.
    """
    import testbed

    captured: dict[str, list[str]] = {}
    # A plain dict in place of the real environment: `exec` sets the component's variables
    # before replacing the process, and this is a test, not a container.
    monkeypatch.setattr(testbed.os, "environ", dict(os.environ))
    monkeypatch.setattr(testbed.os, "execv",
                        lambda _path, argv: captured.__setitem__("argv", argv))

    testbed.exec_component("station-ut", host="0.0.0.0")
    argv = captured["argv"]
    assert argv[argv.index("--host") + 1] == "0.0.0.0"
    assert argv[argv.index("--port") + 1] == str(_named("station-ut").port)
    # and the profile is what configured it, not this file
    assert testbed.os.environ["FDT_STATION_IRI"] == _named("station-ut").identity

    # A process on a developer's machine binds the loopback address and nothing wider.
    testbed.exec_component("depot", host="127.0.0.1")
    argv = captured["argv"]
    assert argv[argv.index("--host") + 1] == "127.0.0.1"


# ------------------------------------------------------------------- is it ours that answered?


def test_the_health_check_asks_about_the_service_it_is_on() -> None:
    """And asks the runner, not the port.

    `testbed.py health` compares the body against the IRI the instance's profile configures, so
    a stray container holding a port is reported as a stray container. A health check that asked
    only whether something answered would pass for anything at all — which is exactly how the
    first run of the process runner reported a FAIR Data Point as a running station.
    """
    for service, definition in _component_services().items():
        test = definition["healthcheck"]["test"]
        assert test[:4] == ["CMD", "python", "deploy/testbed.py", "health"], service
        assert test[4] == service, service


def test_health_answers_no_when_somebody_else_holds_the_port(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """The command every container in this testbed is judged by, asked directly.

    Docker restarts, reports and gates `depends_on` on this exit code, so an implementation that
    could only say yes would make `service_healthy` mean `service_exists`. The distinction it has
    to draw is not hypothetical on a developer's machine: these ports are shared with whatever
    else the person has running, and the first run of the process runner found a FAIR Data Point
    on one of them.
    """
    import testbed

    ut = _named("station-ut")
    monkeypatch.setattr(testbed, "_answers", lambda component, timeout: None)
    assert health("station-ut", timeout=0.1) == 1, "nothing answered, and it said yes"

    somebody_else = "<http://localhost:8400/> a <https://w3id.org/fdp/o#MetadataService> ."
    monkeypatch.setattr(testbed, "_answers", lambda component, timeout: somebody_else)
    assert health("station-ut", timeout=0.1) == 1, "the wrong software answered, and it said yes"

    monkeypatch.setattr(testbed, "_answers",
                        lambda component, timeout: f"<{ut.identity}> a fdt-o:DataStation .")
    assert health("station-ut", timeout=0.1) == 0
    # and it is this station's IRI that is asked for, not any station's
    assert health("station-oosterlicht", timeout=0.1) == 1


def test_nothing_restarts_itself_out_of_sight() -> None:
    """A component that dies in a testbed should be a component that died. Restarting it until
    somebody happens to read the logs turns a reproducible failure into an intermittent one."""
    for service, definition in _services().items():
        assert definition.get("restart") == "no", service


# ------------------------------------------------------------------------------ the front door


def test_the_front_door_points_at_the_ports_the_profiles_configure() -> None:
    """`deploy/docker/console-index.html` is where a person lands, and it carries this testbed's
    addresses because a console holds none of its own — which station, Depot, registry or
    Handler it talks to is a query parameter, so that one build serves whichever instance
    somebody is looking at."""
    page = FRONT_DOOR.read_text(encoding="utf-8")
    linked = {int(port) for port in re.findall(r"localhost:(\d+)", page)}
    assert linked, "the front door links to nothing"
    assert linked <= {component.port for component in components(run_plan=True)}


def test_the_front_door_offers_every_component_a_console_was_written_for() -> None:
    """Both stations, the public catalogue, the Depot, the registry and the Handler. A front
    door that quietly dropped Oosterlicht would take the second regime out of the testbed, which
    is the reason there are two stations."""
    page = FRONT_DOOR.read_text(encoding="utf-8")
    where = {component.name: component.port for component in components(run_plan=True)}
    for bundle, port in (
        ("station.html", where["station-ut"]),
        ("station.html", where["station-oosterlicht"]),
        ("public.html", where["station-ut"]),
        ("depot.html", where["depot"]),
        ("registry.html", where["registry"]),
        ("handler.html", where["handler"]),
    ):
        assert f"/{bundle}?" in page and f"localhost:{port}" in page, (bundle, port)


# ------------------------------------------------------------------ the one that needs Docker


def _docker_or_skip() -> None:
    """Skip, unless the environment said Docker would be here.

    `FDT_REQUIRE_DOCKER=1` turns the skip into a failure, for the same reason
    `FDT_REQUIRE_SIBLINGS` does in the component suites: a check that silently vanishes is worse
    than one that fails, because the suite goes on reporting success.
    """
    if shutil.which("docker") and subprocess.run(  # noqa: S603
        ["docker", "compose", "version"], capture_output=True, check=False,  # noqa: S607
    ).returncode == 0:
        return
    if os.environ.get("FDT_REQUIRE_DOCKER") == "1":
        raise RuntimeError("FDT_REQUIRE_DOCKER=1 but `docker compose` does not run here.")
    pytest.skip("docker compose is not available")


@pytest.mark.parametrize("service,profile", [
    ("station-ut", "station-ut.env"),
    ("station-oosterlicht", "station-oosterlicht.env"),
    ("depot", "depot.env"),
    ("registry", "registry.env"),
    ("handler", "handler.env"),
    ("consoles", "console.env"),
])
def test_compose_reads_a_profile_exactly_as_the_runner_does(service: str, profile: str) -> None:
    """Two parsers, one file — the arrangement's only real risk.

    `deploy/env.py` takes a value verbatim to the end of the line: no quote stripping, no
    `$VAR`, and `#` is not a comment inside a value. Compose has its own `.env` reader with its
    own conveniences, and both of those conveniences would corrupt a profile here — half the
    IRIs in this ecosystem carry a fragment, and `https://w3id.org/fdt/network#StationRole`
    truncated at `#` is a different IRI that still parses, while stripping the quotes from
    `FDT_STATION_CONTROLLER_TOKENS` turns JSON into something that is not JSON.

    They agree today. This is what says so tomorrow.
    """
    _docker_or_skip()
    resolved = json.loads(subprocess.run(  # noqa: S603
        ["docker", "compose", "-f", str(COMPOSE), "config", "--format", "json"],  # noqa: S607
        capture_output=True, check=True, text=True, cwd=str(DEPLOY),
    ).stdout)
    environment = resolved["services"][service]["environment"]
    for key, value in read_profile(PROFILES / profile).items():
        assert environment.get(key) == value, key
