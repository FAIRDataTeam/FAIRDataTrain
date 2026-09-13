# syntax=docker/dockerfile:1.7
#
# One Dockerfile, four component images and one toolbox — `deploy/compose.yaml` picks between
# them with `target:` and the `COMPONENT` build argument.
#
# The build context is the whole metaproject, not a component directory, because an image needs
# both a component and the contracts it validates against: a station that shipped without
# `fdt-commons` would start and then refuse every visit it was given, which is a failure that
# looks like a protocol error and is a packaging one.
#
# **The image reproduces the checkout's layout** — `/fdt/fdt-commons`, `/fdt/FDT-O`,
# `/fdt/deploy`, the component's package installed — so that a profile written for the process
# runner is the same profile here, unedited. `FDT_STATION_DATASETS` names
# `fdt-commons/examples/data/…` relative to the checkout root; with `WORKDIR /fdt` that path
# resolves inside the container too, and a profile that had to be rewritten for containers would
# be a second configuration format pretending to be the first.

ARG PYTHON=3.12-slim


# ── the contracts, shared by every image below ──────────────────────────────────────────────
#
# Identical in all five builds, so Docker builds it once and the rest are layer hits.

FROM python:${PYTHON} AS contracts

WORKDIR /fdt
COPY fdt-commons/ fdt-commons/
COPY FDT-O/ FDT-O/

# Every component finds the contracts and the ontology the same way. Set once here rather than
# in five profiles, where one could drift from the other four — `deploy/testbed.py` sets exactly
# these three for the process runner, for the same reason.
ENV FDT_COMMONS=/fdt/fdt-commons \
    FDT_O=/fdt/FDT-O \
    FDT_STATION_CONTRACTS_DIR=/fdt/fdt-commons \
    PYTHONUNBUFFERED=1


# ── the toolbox: the network namespace, and the seeding ─────────────────────────────────────
#
# `deploy/testbed.py` knows what the testbed is made of and what has to happen once it is up:
# the registry's first harvest, and the one visit at Oosterlicht that puts a case in a
# controller's queue. The compose runs that code rather than a second copy of it in YAML,
# because two accounts of one testbed disagree eventually, and the disagreement is found by
# somebody who has just run it.

FROM contracts AS tools

COPY deploy/ deploy/
CMD ["sleep", "infinity"]


# ── a component ─────────────────────────────────────────────────────────────────────────────

FROM contracts AS component

#: The submodule directory to install — the compose names it per service.
ARG COMPONENT
RUN test -n "${COMPONENT}" || \
    (echo "build arg COMPONENT is required: which component is this an image of?" >&2; false)

COPY ${COMPONENT}/ /build/component/
RUN pip install --no-cache-dir /build/component && rm -rf /build

# The runner comes in too. It is how each service is started and how each is health-checked —
# `testbed.py exec` builds the same argv the process runner builds, from the same profile, and
# `testbed.py health` asks the same question `make status` asks. One definition of what this
# testbed is, used by the processes, by the containers and by the tests.
COPY deploy/ deploy/

# Nothing here writes to the checkout, and a testbed that ran as root would be teaching a
# deployment habit rather than demonstrating a protocol.
RUN useradd --create-home --uid 10001 fdt
USER fdt
