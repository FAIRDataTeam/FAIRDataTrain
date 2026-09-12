# FAIR Data Train — reference implementation
#
# `make check` is the gate: it runs every contract validator in fdt-commons and FDT-O.
# Nothing downstream is trustworthy while it is red, because every component is generated
# from, or tested against, those contracts.

SHELL := /bin/bash
.DEFAULT_GOAL := help

ROOT      := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
VENV      := $(ROOT)/.venv
PY        := $(VENV)/bin/python
PIP       := $(VENV)/bin/pip
COMMONS   := $(ROOT)/fdt-commons
FDTO      := $(ROOT)/FDT-O
CONSOLE   := $(ROOT)/FDTConsole

PY_COMPONENTS := FAIRDataStation-py FAIRDataTrainHandler IndividualGateway FDTRegistry TrainDepot

# The shapes constrain terms the ontology declares, and sh:class follows rdfs:subClassOf*
# in the data graph. Point the fdt-commons checker at the merged ontology explicitly rather
# than letting it guess, so a missing ontology is an error and not a quiet false pass.
export FDT_O_ONTOLOGY := $(FDTO)/ontology/fdt-o.ttl

.PHONY: help
help:  ## show this help
	@echo "FAIR Data Train — reference implementation"
	@echo
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'
	@echo
	@echo "Start with: make submodules && make check"

.PHONY: submodules
submodules:  ## check out every component repository
	@git -C $(ROOT)/.. submodule update --init --recursive

$(VENV):
	@command -v uv >/dev/null 2>&1 \
	  && uv venv --python 3.12 $(VENV) \
	  || python3 -m venv $(VENV)

.PHONY: venv
venv: $(VENV)  ## create the checker virtualenv
	@command -v uv >/dev/null 2>&1 \
	  && uv pip install --quiet --python $(PY) -r $(COMMONS)/requirements.txt \
	  || $(PIP) install --quiet -r $(COMMONS)/requirements.txt
	@$(PY) -c "import pyshacl, rdflib, jsonschema; print('  checker ready:', \
	  'pyshacl', pyshacl.__version__, '· rdflib', rdflib.__version__)"

.PHONY: check
check: check-commons check-ontology  ## run every contract validator (the M0 gate)
	@echo
	@echo "  ✓ contracts green"

.PHONY: check-commons
check-commons: venv  ## validate fdt-commons: shapes, schemas, protocol fixtures, round-trip
	@echo "── fdt-commons ──────────────────────────────────────────────"
	@cd $(COMMONS) && $(PY) tests/validate.py

.PHONY: check-ontology
check-ontology: venv  ## validate FDT-O: instances, counter-examples, fdt-commons cross-check
	@echo
	@echo "── FDT-O ────────────────────────────────────────────────────"
	@cd $(FDTO) && $(PY) tests/validate.py

.PHONY: generate
generate: venv  ## generate models and types from the contracts (WP-0.3)
	@echo "WP-0.3 — not implemented yet."
	@echo "  pydantic models from fdt-commons/schemas/ and protocol/openapi/ for the"
	@echo "  Python components; TypeScript types for the consoles:"
	@cd $(CONSOLE) && npm run generate

# Each component has its own environment with its own dependencies — the checker venv holds
# only pySHACL, rdflib and jsonschema, so running a component's tests from it fails on the
# first import. Build per-component venvs here exactly as CI does.
.PHONY: test
test:  ## run each component's tests, lint and types, in its own environment
	@for c in $(PY_COMPONENTS); do \
	  echo "── $$c ──"; \
	  ( cd $(ROOT)/$$c \
	    && uv venv --quiet --allow-existing --python 3.12 .venv \
	    && uv pip install --quiet --python .venv/bin/python -e ".[dev]" \
	    && { [ "$$c" = TrainDepot ] || uv pip install --quiet --python .venv/bin/python \
	         -e $(ROOT)/TrainDepot; } \
	    && FDT_REQUIRE_DEPOT=1 .venv/bin/pytest -q \
	    && .venv/bin/ruff check src tests \
	    && .venv/bin/mypy --strict src ) || exit 1; \
	done
	@echo
	@echo "── FDTConsole ──"
	@cd $(CONSOLE) \
	  && { [ -d node_modules ] || npm install --silent --no-fund --no-audit; } \
	  && npm run --silent generate \
	  && npm run --silent typecheck

# The scenarios need every component in ONE environment: they run the real Handler against
# the real station, which is the only way either can be shown to agree with the other.
E2E := $(ROOT)/.venv-e2e

.PHONY: e2e
e2e:  ## run the milestone scenarios with the real components against each other
	@echo "── end-to-end ───────────────────────────────────────────────"
	@uv venv --quiet --allow-existing --python 3.12 $(E2E)
	@uv pip install --quiet --python $(E2E)/bin/python pytest \
	  -e $(ROOT)/FAIRDataStation-py -e $(ROOT)/FAIRDataTrainHandler -e $(ROOT)/TrainDepot
	@$(E2E)/bin/pytest -q $(ROOT)/tests/e2e
	@echo
	@echo "  M1 one visit ✓ · M2 fan-out and governance · M3 multi-hop · M4 composition"

.PHONY: up
up:  ## bring up the demo stations
	@echo "Not implemented yet — deploy/compose/ lands with WP-1.4."
	@exit 1

.PHONY: clean
clean:  ## remove the checker virtualenv
	@rm -rf $(VENV)
