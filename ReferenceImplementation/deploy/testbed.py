"""Bring the testbed up: two stations, a Depot, a registry, a Handler and the consoles.

This is what WP-5.5's acceptance criterion needs — "the M1 scenario watched end to end in a
browser" — and until now there was no way to run one. `make up` printed "not implemented yet".

**Processes, not containers.** Every component is a Python package in this checkout with a
`serve` command and settings read from the environment, so the shortest path from a working
tree to something you can click on is to start six of them. Containers are a packaging question
(WP-4.3) and would put a build between every edit and the browser, which is the opposite of
what a testbed is for.

**Each instance is a profile in `deploy/profiles/`**, read by `deploy/env.py` and handed to the
subprocess as its environment. Nothing is configured here in code: a station that behaved
differently under the testbed than under its own settings file would be demonstrating the
testbed rather than the station.

**The two stations differ on the thing the architecture is about.** The UT station's network
permits a machine to conclude a negotiation; Oosterlicht is also in a network that does not, so
it decides nothing in either direction there and puts the case to a person (ADR-032). A testbed
with one station would show the automated path and quietly imply it was the only one.

Ctrl-C stops everything. A component that dies is reported with its last output rather than
leaving a URL in the table that answers nothing.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from env import read_profile  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "deploy" / "profiles"
COMMONS = ROOT / "fdt-commons"
ONTOLOGY = ROOT / "FDT-O"

#: The plan the M1 scenario runs, and the one the acceptance criterion names.
PLAN = COMMONS / "examples" / "plan-gene-disease-single.jsonld"

STATION_IRI = "https://example.org/fdt/station/ut"
HANDLER_IRI = "https://handler.cardionet.example/fdt/v1"


@dataclass
class Component:
    """One process in the testbed."""

    name: str
    #: The component checkout, whose `.venv` runs it. `make test` builds these.
    package: str
    argv: list[str]
    port: int
    #: A string that must appear in the health response for this to be **our** component.
    #:
    #: A port that answers is not the same fact as the thing we started answering, and the
    #: difference is not academic: the first run of this script reported a Docker container
    #: somebody had left on 8000 as a healthy station. Every component publishes its own IRI at
    #: `/`, so the check costs one string search.
    #:
    #: **Required, with no default.** A default of `""` is in every body there is, including an
    #: empty one, so a component that forgot to set it would have the check silently turned off
    #: — which is the failure this field exists to prevent, arriving by another door. A mutation
    #: run made exactly that substitution and no test noticed.
    identity: str
    #: A path that answers once the component is up.
    health: str = "/"
    profile: str | None = None
    extra: dict[str, str] = field(default_factory=dict)
    process: subprocess.Popen[bytes] | None = None
    log: Path | None = None

    @property
    def url(self) -> str:
        return f"http://localhost:{self.port}"


def _resolve(values: dict[str, str]) -> dict[str, str]:
    """Make the profile's repo-relative paths absolute.

    A profile names `fdt-commons/examples/data/…` because that is where the file is in this
    checkout, and a subprocess started from anywhere would not find it. Substituting the
    absolute prefix here keeps the profile readable and keeps the runner from having to know
    which keys hold paths.
    """
    prefix = str(COMMONS) + "/"
    return {key: value.replace("fdt-commons/", prefix) for key, value in values.items()}


def _environment(component: Component) -> dict[str, str]:
    environment = dict(os.environ)
    # Every component finds the contracts and the ontology the same way, so this is set once
    # rather than repeated in five profiles where one could drift from the rest.
    environment["FDT_COMMONS"] = str(COMMONS)
    environment["FDT_O"] = str(ONTOLOGY)
    environment["FDT_STATION_CONTRACTS_DIR"] = str(COMMONS)
    if component.profile:
        environment.update(_resolve(read_profile(PROFILES / component.profile)))
    environment.update(component.extra)
    return environment


#: profile → (name, package, module, the profile key holding the IRI it must publish).
_FROM_PROFILE = (
    ("station-ut.env", "station-ut", "FAIRDataStation-py", "fdt_station", "FDT_STATION_IRI"),
    ("station-oosterlicht.env", "station-oosterlicht", "FAIRDataStation-py", "fdt_station",
     "FDT_STATION_IRI"),
    ("depot.env", "depot", "TrainDepot", "fdt_depot", "FDT_DEPOT_IRI"),
    # The registry is last of the four so that its first harvest finds its sources. It would
    # survive starting first — an unreachable source is a row that says so, not a crash — but a
    # testbed whose registry opens on two failed harvests teaches the wrong lesson on the first
    # screen somebody looks at.
    ("registry.env", "registry", "FDTRegistry", "fdt_registry", "FDT_REGISTRY_IRI"),
)

HANDLER_PORT = 8404


def components(*, run_plan: bool) -> list[Component]:
    """The testbed, in start order: what is harvested before what harvests it."""
    listed = []
    for profile, name, package, module, identity_key in _FROM_PROFILE:
        values = read_profile(PROFILES / profile)
        port = int(values["FDT_TESTBED_PORT"])
        listed.append(Component(
            name=name, package=package, port=port,
            argv=["-m", module, "serve", "--host", "127.0.0.1", "--port", str(port)],
            identity=values[identity_key],
            profile=profile,
        ))
    if run_plan:
        station = read_profile(PROFILES / "station-ut.env")
        listed.append(Component(
            name="handler", package="FAIRDataTrainHandler", port=HANDLER_PORT,
            argv=[
                "-m", "fdt_handler", "serve", str(PLAN),
                # The station's IRI is not resolvable; `--at` says where it actually is. The
                # URL comes from the station's own profile, so the two cannot drift.
                "--at", f"{station['FDT_STATION_IRI']}={station['FDT_STATION_BASE_URL']}",
                "--handler", HANDLER_IRI,
                "--agent", "m.devries@cardionet.example",
                "--contracts", str(COMMONS),
                "--host", "127.0.0.1", "--port", str(HANDLER_PORT),
            ],
            identity=HANDLER_IRI,
        ))
    return listed


def _free(port: int) -> bool:
    with socket.socket() as probe:
        return probe.connect_ex(("127.0.0.1", port)) != 0


def _answers(component: Component, *, timeout: float) -> str | None:
    """The body `component` serves at its health path, or `None` if it does not answer."""
    try:
        with urllib.request.urlopen(  # noqa: S310 — localhost, a URL we composed
            f"{component.url}{component.health}", timeout=timeout
        ) as answer:
            if answer.status >= 500:
                return None
            return answer.read(65536).decode("utf-8", errors="replace")
    except (urllib.error.URLError, OSError):
        return None


def _is_ours(component: Component, body: str | None) -> bool:
    """Does the thing answering publish the IRI this component was configured with?

    Every component serves its own IRI at `/` — the station as RDF, the others as JSON — so
    this is the cheapest possible identity check and it is not optional. Without it a port
    somebody else's process is holding reads as a healthy component, which is exactly how the
    first run of this script reported a stray Docker container as a running station.
    """
    return body is not None and component.identity in body


def _healthy(component: Component, *, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if component.process is not None and component.process.poll() is not None:
            return False
        if _is_ours(component, _answers(component, timeout=1.0)):
            return True
        time.sleep(0.2)
    return False


def _tail(component: Component, lines: int = 12) -> str:
    if component.log is None or not component.log.exists():
        return "(no output)"
    return "\n".join(f"      {line}" for line in
                     component.log.read_text(errors="replace").splitlines()[-lines:])


def up(logs: Path, *, run_plan: bool, timeout: float) -> int:
    logs.mkdir(parents=True, exist_ok=True)
    started: list[Component] = []

    def stop() -> None:
        for component in reversed(started):
            if component.process and component.process.poll() is None:
                component.process.terminate()
        for component in reversed(started):
            if component.process:
                try:
                    component.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    component.process.kill()

    for component in components(run_plan=run_plan):
        python = ROOT / component.package / ".venv" / "bin" / "python"
        if not python.exists():
            print(f"  {component.name}: no environment at {python}.", file=sys.stderr)
            print("  Run `make test` once to build them, then try again.", file=sys.stderr)
            stop()
            return 1
        if not _free(component.port):
            print(f"  {component.name}: port {component.port} is already in use.",
                  file=sys.stderr)
            stop()
            return 1

        component.log = logs / f"{component.name}.log"
        handle = component.log.open("wb")
        component.process = subprocess.Popen(  # noqa: S603 — our own argv, no shell
            [str(python), *component.argv],
            cwd=str(ROOT), env=_environment(component), stdout=handle, stderr=handle,
        )
        started.append(component)
        if _healthy(component, timeout=timeout):
            print(f"  up    {component.name:<22} {component.url}")
            _after_start(component)
        else:
            print(f"  FAILED {component.name:<21} {component.url}", file=sys.stderr)
            print(_tail(component), file=sys.stderr)
            stop()
            return 1

    _print_urls(run_plan=run_plan)
    print("\n  Ctrl-C to stop. Logs in", logs.relative_to(ROOT))
    try:
        while True:
            for component in started:
                if component.process and component.process.poll() is not None:
                    print(f"\n  {component.name} exited "
                          f"({component.process.returncode}):", file=sys.stderr)
                    print(_tail(component), file=sys.stderr)
                    stop()
                    return 1
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n  stopping…")
        stop()
        return 0


#: The visit the testbed seeds at Oosterlicht, and the network that makes it interesting.
STROKE_OOST = "https://example.org/fdt/net/stroke-oost"
OOSTERLICHT_DATA = "https://example.org/fdt/dataset/oosterlicht-gene-disease"
SEEDED_VISIT = "https://example.org/fdt/visit/testbed-oost-1"


def _seed_an_approval(station: Component) -> None:
    """One visit at Oosterlicht **under the Oost network**, which nobody may decide by machine.

    Without it console S3 is an empty queue and ADR-032 is a paragraph. With it the testbed shows
    the thing the second station is there for: the same request that is granted automatically at
    the UT station is, in a network whose regime bars automated authorisation, neither granted
    nor refused — the station evaluates it, recommends, and puts the case with its evidence to a
    person, who is the only one who may conclude it.

    The descriptor is `visit-descriptor-gd-m1.json` re-aimed at Oosterlicht's dataset and that
    network, exactly as `tests/e2e/test_two_regimes.py` re-aims it. Nothing else about it is
    invented here: a testbed that made up a request would be demonstrating the request.
    """
    source = COMMONS / "examples" / "protocol" / "visit-descriptor-gd-m1.json"
    descriptor = json.loads(source.read_text())
    descriptor["visit"] = SEEDED_VISIT
    descriptor["target"] = OOSTERLICHT_DATA
    descriptor["network"] = STROKE_OOST
    # Poll, not push: there is no Handler waiting to be called back about this one.
    descriptor["reporting"] = {"mode": "poll"}
    descriptor["negotiation"]["request"]["target"] = OOSTERLICHT_DATA
    descriptor["negotiation"]["request"]["underNetwork"] = STROKE_OOST

    request = urllib.request.Request(
        f"{station.url}/visits", method="POST",
        data=json.dumps(descriptor).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as answer:  # noqa: S310
            state = json.loads(answer.read()).get("state")
    except (urllib.error.URLError, OSError, ValueError) as failed:
        print(f"        no approval seeded: {failed}", file=sys.stderr)
        return
    print(f"        seeded one visit under {STROKE_OOST.rsplit('/', 1)[-1]} — {state}; "
          f"it is in the controller's queue, not decided")


def _after_start(component: Component) -> None:
    """The registry harvests once, now that its sources are up.

    A registry does not harvest at start-up, and should not: an unreachable station would become
    a reason the registry cannot run, when reporting that the station is unreachable is the job.
    But a testbed whose registry opens on an empty index teaches the wrong lesson on the first
    screen somebody looks at, so the runner does what an operator would do and asks it to
    harvest — which is a POST anybody can make, and is visible in the console as a harvest time.
    """
    if component.name == "station-oosterlicht":
        _seed_an_approval(component)
        return
    if component.name != "registry":
        return
    try:
        request = urllib.request.Request(f"{component.url}/harvest", method="POST")
        with urllib.request.urlopen(request, timeout=60) as answer:  # noqa: S310
            reports = json.loads(answer.read())
    except (urllib.error.URLError, OSError, ValueError) as failed:
        print(f"        first harvest did not run: {failed}", file=sys.stderr)
        return
    for report in reports:
        if report.get("reached"):
            print(f"        harvested {report['kind']:<8} {report['url']} — "
                  f"{report.get('stations', 0)} station(s), {report.get('trains', 0)} train(s)")
        else:
            # Not fatal. A registry exists to report exactly this, and hiding it here would
            # make the testbed less honest than the thing it is running.
            print(f"        UNREACHED {report['kind']:<8} {report['url']} — "
                  f"{report.get('error')}", file=sys.stderr)


def _print_urls(*, run_plan: bool) -> None:
    print("\n  The consoles — `npm run dev` in FDTConsole, then:\n")
    dev = "http://localhost:5173"
    where = {component.name: component.url for component in components(run_plan=True)}
    rows = [
        ("Station · UT", f"{dev}/station.html?station={where['station-ut']}"),
        ("Station · Oosterlicht", f"{dev}/station.html?station={where['station-oosterlicht']}"),
        ("Public catalogue (S9)", f"{dev}/public.html?station={where['station-ut']}"),
        ("Depot", f"{dev}/depot.html?depot={where['depot']}"),
        ("Registry", f"{dev}/registry.html?registry={where['registry']}"),
    ]
    if run_plan:
        # H1 and H2 read a registry and follow it to the Depot; H3 and H4 read the Handler.
        # Three components on one page, which is why the console addresses them separately.
        rows.append((
            "Handler",
            f"{dev}/handler.html?handler={where['handler']}"
            f"&registry={where['registry']}",
        ))
    for label, url in rows:
        print(f"    {label:<24} {url}")
    print("\n    The station console's operator credential is `testbed-operator`"
          " (Settings → S8);")
    print("    Oosterlicht's controller credential, for the approvals queue, is"
          " `testbed-controller`.")


def status(timeout: float) -> int:
    """Is each component answering — and is the thing answering ours?"""
    code = 0
    for component in components(run_plan=True):
        body = _answers(component, timeout=timeout)
        if body is None:
            print(f"  down     {component.name:<22} {component.url}")
            code = 1
        elif _is_ours(component, body):
            print(f"  up       {component.name:<22} {component.url}")
        else:
            # The distinction the first version of this script did not draw.
            print(f"  SOMEBODY ELSE {component.name:<17} {component.url} — something is "
                  f"listening but it does not publish {component.identity}")
            code = 1
    return code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="testbed", description=__doc__)
    parser.add_argument("command", nargs="?", default="up", choices=["up", "status"])
    parser.add_argument("--no-plan", action="store_true",
                        help="do not start the Handler, which drives the M1 plan on startup")
    parser.add_argument("--timeout", type=float, default=30.0,
                        help="seconds to wait for each component to answer")
    parser.add_argument("--logs", default=str(ROOT / ".testbed"),
                        help="where to write each component's output")
    args = parser.parse_args(argv)

    if args.command == "status":
        return status(args.timeout)

    print("  Bringing up the FDT testbed.\n")
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    return up(Path(args.logs), run_plan=not args.no_plan, timeout=args.timeout)


if __name__ == "__main__":
    sys.exit(main())
