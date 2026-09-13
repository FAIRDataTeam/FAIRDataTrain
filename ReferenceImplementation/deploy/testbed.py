"""Bring the testbed up: two stations, a Depot, a registry, a Handler and the consoles.

This is what WP-5.5's acceptance criterion needs — "the M1 scenario watched end to end in a
browser" — and until now there was no way to run one. `make up` printed "not implemented yet".

**Two ways to run it, one definition of what it is.** `deploy/compose.yaml` runs the testbed
as containers, which is what you want when you are looking at the ecosystem; this file also
starts the same components as processes out of the checkout (`make up-processes`), which is what
you want when you are changing one, because a container build stands between every edit and the
screen.

Both go through `components()`. The compose does not repeat an argument, a port or an identity
in YAML: each service runs `testbed.py exec <name>` and is health-checked with
`testbed.py health <name>`, so there is one account of what this testbed is made of and both
ways of running it are that account. Two accounts of one testbed disagree eventually, and the
disagreement is found by somebody who has just run it.

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

Commands
--------
`up`      start the components as processes and hold them (`make up-processes`)
`status`  is each one answering, and is the thing answering ours (`make status`)
`ready`   wait for all of them, then print the table and the console URLs (`make up`)
`seed`    the registry's first harvest and the one visit in a controller's queue
`exec`    become one component — how each container starts
`health`  is that one component ours — how each container is health-checked
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

    `.testbed/` is the other prefix: runtime state a component writes rather than reads. It
    resolves to the same place under both ways of running this testbed — the checkout on a
    developer's machine, and `/fdt/.testbed` inside a container, which the image creates and
    owns so the unprivileged user can write there. Compose declares no volume, so a container's
    is gone with the container, which is what "`make down && make up` is a clean testbed" means.
    """
    prefixes = {"fdt-commons/": str(COMMONS) + "/", ".testbed/": str(ROOT / ".testbed") + "/"}
    resolved = {}
    for key, value in values.items():
        for prefix, absolute in prefixes.items():
            value = value.replace(prefix, absolute)
        resolved[key] = value
    return resolved


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

def components(*, run_plan: bool, host: str = "127.0.0.1") -> list[Component]:
    """The testbed, in start order: what is harvested before what harvests it.

    `host` is what each component binds. The default is the loopback address, which is what a
    process on a developer's machine should bind and never anything wider. A container binds
    `0.0.0.0` instead — its own network namespace, which is the testbed's and nothing beyond it,
    because `deploy/compose.yaml` publishes those ports on the loopback address only.
    """
    listed = []
    for profile, name, package, module, identity_key in _FROM_PROFILE:
        values = read_profile(PROFILES / profile)
        port = int(values["FDT_TESTBED_PORT"])
        listed.append(Component(
            name=name, package=package, port=port,
            argv=["-m", module, "serve", "--host", host, "--port", str(port)],
            identity=values[identity_key],
            profile=profile,
        ))
    if run_plan:
        handler = read_profile(PROFILES / "handler.env")
        station = read_profile(PROFILES / "station-ut.env")
        port = int(handler["FDT_TESTBED_PORT"])
        listed.append(Component(
            name="handler", package="FAIRDataTrainHandler", port=port,
            argv=[
                "-m", "fdt_handler", "serve",
                str(ROOT / handler["FDT_HANDLER_PLAN"]),
                # The station's IRI is not resolvable; `--at` says where it actually is. The
                # URL comes from the station's own profile, so the two cannot drift.
                "--at", f"{station['FDT_STATION_IRI']}={station['FDT_STATION_BASE_URL']}",
                "--handler", handler["FDT_HANDLER_IRI"],
                "--agent", handler["FDT_HANDLER_AGENT"],
                "--contracts", str(COMMONS),
                # A Handler has no settings class, so what every other component reads from its
                # profile the Handler is told on the command line — from the same profile.
                *[
                    argument
                    for origin in handler["FDT_HANDLER_CORS_ORIGINS"].split(",")
                    if origin.strip()
                    for argument in ("--allow-origin", origin.strip())
                ],
                "--host", host, "--port", str(port),
            ],
            identity=handler["FDT_HANDLER_IRI"],
            # Read for the four values above rather than exported: a Handler has no settings
            # class, because it is configured by the plan it is given and the arguments it is
            # dispatched with.
        ))
    return listed


def _named(name: str, *, host: str = "127.0.0.1") -> Component:
    """The one component called `name`, or an error naming the ones there are.

    `host` is passed through to `components()`, and dropping it here is not a cosmetic mistake:
    the first run of the compose bound every component to the loopback address inside its
    container, where the health check — which asks 127.0.0.1 from inside that same namespace —
    reported all five healthy while nothing on the host could reach any of them. A container can
    always talk to itself. `make up`'s own table is what noticed, because it asks from outside.
    """
    for component in components(run_plan=True, host=host):
        if component.name == name:
            return component
    known = ", ".join(c.name for c in components(run_plan=True))
    raise SystemExit(f"no component called {name!r} in this testbed. There is: {known}")


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
        # Both start paths mint, because there are two of them and only one is exercised by
        # `make up`. A Depot configured with a creator key set and unable to read it refuses to
        # start, by design — so a runner that minted in the container path alone would leave
        # `make up-processes` failing on a file the other path creates.
        environment = _environment(component)
        _mint_creator_keys(environment)
        component.process = subprocess.Popen(  # noqa: S603 — our own argv, no shell
            [str(python), *component.argv],
            cwd=str(ROOT), env=environment, stdout=handle, stderr=handle,
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
    if component.name == "depot":
        _publish_a_train(component)
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


def _publish_a_train(depot: Component) -> None:
    """One train published by its creator, so the Depot's write surface is on the testbed.

    WP-5.5's acceptance criterion asks for *a train published to the Depot and found through the
    registry by its data requirement*, and until this ran there was no published train to find:
    every train the Depot served came from the corpus it was deployed with, which demonstrates
    resolving a train and not publishing one (ADR-036).

    The Depot ordering matters and is not incidental — `components()` yields the Depot before the
    registry, so the train is in the Depot before the registry's first harvest and the index opens
    with it in. A registry that had to be harvested twice to show it would teach that publishing is
    slow, which is a fact about this runner rather than about the ecosystem.
    """
    import creator                                       # deploy/, on the path beside this file

    print(f"        {creator.publish(depot.url, COMMONS)}")


def _print_urls(*, run_plan: bool, consoles: str | None = None) -> None:
    """Where to look. `consoles` is the address the console bundles are served from.

    Under the compose that is a container of this testbed's own, and the URLs below are live the
    moment the table above is. Under the process runner it is `npm run dev` on the host, which
    is a thing a person still has to start — so the line says so rather than printing an address
    that answers nothing.
    """
    dev = consoles or "http://localhost:5173"
    if consoles:
        print(f"\n  The consoles — {consoles}, or straight to one of them:\n")
    else:
        print("\n  The consoles — `npm run dev` in FDTConsole, then:\n")
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


def exec_component(name: str, host: str) -> int:
    """Become the named component: how each container in `deploy/compose.yaml` starts.

    The compose says `testbed.py exec station-ut` and nothing else — no argument, no port, no
    path. All of it comes from the same `components()` the process runner uses, and the
    environment from the same `deploy/env.py` that reads the profile, so a container and a
    process are two ways of running one description rather than two descriptions.

    `os.execv` rather than a subprocess: the component becomes PID 1's process, so Docker's
    stop signal reaches uvicorn instead of a wrapper that would have to forward it.
    """
    component = _named(name, host=host)
    environment = _environment(component)
    for key, value in environment.items():
        os.environ[key] = value
    _mint_creator_keys(environment)
    os.execv(sys.executable, [sys.executable, *component.argv])  # noqa: S606 — our own argv


def _mint_creator_keys(environment: dict[str, str]) -> None:
    """Write the Depot's creator key set, if it was configured with one and has none.

    It has to exist *before* the Depot starts: `CreatorKeys.load` runs at application start-up and
    a Depot told where its keys are and unable to read them refuses to start — deliberately,
    because starting anyway would refuse every creator's signature as an unknown key and send
    whoever is publishing off to check their own key material.

    `deploy/creator.py` derives it, so the container that holds the public half and the container
    that signs with the private half agree without sharing a filesystem. The compose has no
    volumes on purpose, and this is what it costs to keep it that way.
    """
    configured = environment.get("FDT_DEPOT_CREATOR_KEYS")
    if not configured:
        return
    path = Path(configured)
    if path.is_file():
        return
    import creator                                       # deploy/, on the path beside this file

    creator.write_key_set(path)


def health(name: str, timeout: float) -> int:
    """Is the named component answering, and is the thing answering ours?

    Each container's health check, and the same question `status` asks — one implementation.
    A health check that asked only whether the port answered would pass for anything at all,
    which is how the first run of this runner reported a stray container as a running station.
    """
    component = _named(name)
    return 0 if _is_ours(component, _answers(component, timeout=timeout)) else 1


def seed(timeout: float) -> int:
    """The registry's first harvest, and the one visit in a controller's queue.

    Run by the compose's `seed` service once every component is healthy, and by the process
    runner inline as each one comes up. Both call `_after_start`, so what a container testbed
    opens on and what a process testbed opens on are the same thing.
    """
    for component in components(run_plan=False):
        if not _healthy(component, timeout=timeout):
            print(f"  {component.name}: not answering at {component.url}; nothing seeded",
                  file=sys.stderr)
            return 1
        _after_start(component)
    return 0


def ready(timeout: float, *, consoles: str | None) -> int:
    """Wait for every component, then say where to look — `make up`, after the compose.

    Waits rather than probes once. `docker compose up --detach` returns when the containers have
    been created, which is a different fact from the ecosystem being up, and a table printed
    between those two moments says `down` about components that are three seconds from healthy.
    """
    code = 0
    for component in components(run_plan=True):
        if _healthy(component, timeout=timeout):
            print(f"  up    {component.name:<22} {component.url}")
        else:
            body = _answers(component, timeout=1.0)
            if body is None:
                print(f"  DOWN  {component.name:<22} {component.url}", file=sys.stderr)
            else:
                print(f"  SOMEBODY ELSE {component.name:<14} {component.url} — something is "
                      f"listening but it does not publish {component.identity}", file=sys.stderr)
            code = 1
    if code == 0:
        _print_urls(run_plan=True, consoles=consoles)
    return code


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
    parser.add_argument("command", nargs="?", default="up",
                        choices=["up", "status", "ready", "seed", "exec", "health"])
    parser.add_argument("name", nargs="?",
                        help="which component, for `exec` and `health`")
    parser.add_argument("--no-plan", action="store_true",
                        help="do not start the Handler, which drives the M1 plan on startup")
    parser.add_argument("--host", default="127.0.0.1",
                        help="the address `exec` binds (a container binds 0.0.0.0)")
    parser.add_argument("--consoles",
                        help="where the console bundles are served from, if they already are")
    parser.add_argument("--timeout", type=float, default=30.0,
                        help="seconds to wait for each component to answer")
    parser.add_argument("--logs", default=str(ROOT / ".testbed"),
                        help="where to write each component's output")
    args = parser.parse_args(argv)

    if args.command in {"exec", "health"} and not args.name:
        parser.error(f"`{args.command}` needs the name of a component")

    if args.command == "status":
        return status(args.timeout)
    if args.command == "ready":
        return ready(args.timeout, consoles=args.consoles)
    if args.command == "seed":
        return seed(args.timeout)
    if args.command == "exec":
        return exec_component(args.name, args.host)
    if args.command == "health":
        return health(args.name, args.timeout)

    print("  Bringing up the FDT testbed.\n")
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    return up(Path(args.logs), run_plan=not args.no_plan, timeout=args.timeout)


if __name__ == "__main__":
    sys.exit(main())
