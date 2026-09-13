"""What a browser does, which no test client here had ever done.

Every console is served from one origin and reads components on others — the Handler's console
reads a Handler, a registry and a Depot on one page, so it cannot be same-origin with all of
them however it is deployed. A browser therefore refuses each of those requests unless the
component says, in a header, that the page's origin may read it.

Nothing in this repository had ever asked for that header. `TestClient` and `httpx` have no
same-origin policy, so every test passed while every console, opened in a browser against a live
component, reported that the component did not answer. The consoles had never worked, and the
suites could not have told anybody: the request a test makes and the request a browser makes
differed in one header nothing looked at.

So these tests send the header a browser sends. The **preflight** matters as much as the simple
request: a console reading the operator's visit list sends `Authorization`, and a browser will
not send a request carrying that header until an `OPTIONS` has come back naming it. A component
that answered `GET` cross-origin but not its preflight would serve the public catalogue and
refuse every screen behind a credential — which is a failure that looks like a wrong password.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator

import pytest
from conftest import COMMONS, STATION_IRI, STATION_URL
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fdt_depot.api import build_app as build_depot
from fdt_depot.core.config import DepotSettings
from fdt_depot.core.contracts import Contracts as DepotContracts
from fdt_handler.api import build_app as build_handler
from fdt_handler.contracts import Contracts as HandlerContracts
from fdt_handler.runs import RunStore
from fdt_registry.api import build_app as build_registry
from fdt_registry.core.config import RegistrySettings, Source, SourceKind
from fdt_registry.core.contracts import Contracts as RegistryContracts
from fdt_registry.harvest.harvester import Harvester
from fdt_station.app import create_app
from fdt_station.core.config import StationSettings

ONTOLOGY = COMMONS.parent / "FDT-O"

#: Where a console is served from. Not the same origin as any component, which is the point.
CONSOLE = "http://localhost:8405"
SOMEWHERE_ELSE = "https://pages.example.invalid"


def _station(origins: tuple[str, ...]) -> FastAPI:
    return create_app(StationSettings(
        iri=STATION_IRI, base_url=STATION_URL, contracts_dir=COMMONS,
        auth_required=False, admin_token="testbed-operator", cors_origins=origins,
    ))


def _depot(origins: tuple[str, ...]) -> FastAPI:
    return build_depot(
        DepotSettings(iri="https://depot.example.org/fdt/v1", contracts_dir=COMMONS,
                      ontology_dir=ONTOLOGY, cors_origins=origins),
        DepotContracts(COMMONS, ONTOLOGY),
    )


def _registry(origins: tuple[str, ...]) -> FastAPI:
    settings = RegistrySettings(
        iri="https://registry.example/fdt/v1", contracts_dir=COMMONS, ontology_dir=ONTOLOGY,
        sources=(Source(url=STATION_URL, kind=SourceKind.STATION),), cors_origins=origins,
    )
    contracts = RegistryContracts(COMMONS, ONTOLOGY)
    return build_registry(settings, contracts, harvester=Harvester(settings, contracts))


def _handler(origins: tuple[str, ...]) -> FastAPI:
    return build_handler(HandlerContracts(COMMONS, ONTOLOGY), RunStore(), cors_origins=origins)


#: Each component, built one at a time — so that a test naming one really exercises that one.
BUILD: dict[str, Callable[[tuple[str, ...]], FastAPI]] = {
    "station": _station, "depot": _depot, "registry": _registry, "handler": _handler,
}
BASE = {
    "station": STATION_URL, "depot": "http://depot.test",
    "registry": "http://registry.test", "handler": "http://handler.test",
}


def _components(origins: tuple[str, ...]) -> Iterator[dict[str, TestClient]]:
    """One of each component, configured to allow `origins` and nothing else."""
    clients = {
        name: TestClient(build(origins), base_url=BASE[name]) for name, build in BUILD.items()
    }
    yield clients
    for client in clients.values():
        client.close()


@pytest.fixture
def open_to_the_console() -> Iterator[dict[str, TestClient]]:
    yield from _components((CONSOLE,))


@pytest.fixture
def open_to_nobody() -> Iterator[dict[str, TestClient]]:
    yield from _components(())


COMPONENTS = ["station", "depot", "registry", "handler"]


@pytest.mark.parametrize("component", COMPONENTS)
def test_a_console_may_read_a_component_it_is_not_served_by(
    open_to_the_console: dict[str, TestClient], component: str
) -> None:
    """The request the console actually makes, with the header a browser actually attaches.

    Without the answering header the browser discards the response before the page sees it, and
    the console reports that the component did not answer — indistinguishable, on screen, from a
    component that is down.
    """
    answer = open_to_the_console[component].get("/", headers={"Origin": CONSOLE})
    assert answer.status_code == 200
    assert answer.headers.get("access-control-allow-origin") == CONSOLE, component


@pytest.mark.parametrize("component", COMPONENTS)
def test_a_page_from_anywhere_else_is_not_let_in(
    open_to_the_console: dict[str, TestClient], component: str
) -> None:
    """An allow-list that allows everybody is not one. The response body is unchanged — a
    server cannot unsend what it sent — but the browser is not told the page may read it, which
    is the whole mechanism."""
    answer = open_to_the_console[component].get("/", headers={"Origin": SOMEWHERE_ELSE})
    assert answer.headers.get("access-control-allow-origin") != SOMEWHERE_ELSE, component


@pytest.mark.parametrize("component", COMPONENTS)
def test_a_component_told_of_no_console_admits_none(
    open_to_nobody: dict[str, TestClient], component: str
) -> None:
    """The default, and it is closed.

    The same-origin policy is a browser's rule about pages, not a server's rule about clients:
    the Handler still dispatches visits and the registry still harvests catalogues with nothing
    configured here. Opening a component to pages is a separate act, and taking it on an
    operator's behalf would mean every deployment of this software shipped readable by any page
    on the web.
    """
    answer = open_to_nobody[component].get("/", headers={"Origin": CONSOLE})
    assert answer.status_code == 200, "a machine client is unaffected by any of this"
    assert "access-control-allow-origin" not in answer.headers, component


def test_the_preflight_for_a_credentialed_screen_names_the_header_it_carries(
    open_to_the_console: dict[str, TestClient],
) -> None:
    """S1, S2, S3 and S7 all send `Authorization`, and a browser asks permission first.

    A component that answered the simple `GET` cross-origin but refused this would serve the
    public catalogue and fail every screen behind a credential, which on screen looks like a
    rejected credential rather than a missing header.
    """
    answer = open_to_the_console["station"].options(
        "/admin/events",
        headers={
            "Origin": CONSOLE,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )
    assert answer.status_code == 200
    assert answer.headers["access-control-allow-origin"] == CONSOLE
    allowed = answer.headers.get("access-control-allow-headers", "").lower()
    assert "authorization" in allowed


def test_the_credential_still_decides_what_the_browser_is_shown(
    open_to_the_console: dict[str, TestClient],
) -> None:
    """Letting a page make the request is not letting it read the answer.

    Cross-origin permission and authorisation are different questions, and a component that
    conflated them would publish one consumer's traffic to the next the moment a console origin
    was configured. The operator's credential decides, exactly as it did before.
    """
    station = open_to_the_console["station"]
    assert station.get("/admin/events", headers={"Origin": CONSOLE}).status_code == 401
    allowed = station.get(
        "/admin/events",
        headers={"Origin": CONSOLE, "Authorization": "Bearer testbed-operator"},
    )
    assert allowed.status_code == 200
    assert allowed.headers.get("access-control-allow-origin") == CONSOLE


def test_a_cookie_is_never_what_authorises_one_of_these_requests(
    open_to_the_console: dict[str, TestClient],
) -> None:
    """`allow_credentials` is off, deliberately.

    These APIs are authorised by a bearer token the console puts in a header. With credentials
    on, a browser would attach cookies to cross-origin requests and any page an operator happened
    to be visiting could drive their station using their session — the console gains nothing from
    it, because it has no cookies to send.
    """
    for name, client in open_to_the_console.items():
        answer = client.get("/", headers={"Origin": CONSOLE})
        assert "access-control-allow-credentials" not in answer.headers, name


@pytest.mark.parametrize("component", COMPONENTS)
def test_an_origin_that_is_not_one_is_refused_by_every_component(component: str) -> None:
    """`http://localhost:8405/` — the form anybody copies out of an address bar.

    A browser sends `scheme://host[:port]` as the `Origin` header and nothing else, so a
    trailing slash matches no request ever made. Its only symptom would be a console reporting
    that the component did not answer, which is precisely the symptom this setting exists to
    remove: a configuration that looks done and changes nothing.

    All four, because all four are configured by a person typing an address, and a component
    that shrugged at it would be the one that silently stayed shut.
    """
    for written in (
        "http://localhost:8405/",        # the form anybody copies out of an address bar
        "localhost:8405",                # no scheme at all
        "//localhost:8405",              # a scheme-relative URL: netloc, and nothing to say how
        "http://localhost:8405/app",     # a path, which an Origin header never carries
        "http://localhost:8405?dev=1",   # and a query, likewise
    ):
        with pytest.raises(ValueError, match="not a browser origin"):
            BUILD[component]((written,))
