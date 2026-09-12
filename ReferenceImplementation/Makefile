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

PY_COMPONENTS := FAIRDataStation-py FAIRDataTrainHandler IndividualGateway StationDirectory TrainGarage

# The shapes constrain terms the ontology declares, and sh:class follows rdfs:subClassOf*
# in the data graph. Point the fdt-commons checker at the merged ontology explicitly rather
# than letting it guess, so a missing ontology is an error and not a quiet false pass.
export FDT_O_DELTA := $(FDTO)/ontology/fdt-o-v2-delta.ttl

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

.PHONY: test
test: venv  ## run each component's unit tests
	@for c in $(PY_COMPONENTS); do \
	  echo "── $$c ──"; \
	  ( cd $(ROOT)/$$c && $(PY) -m pytest -q ) || exit 1; \
	done

.PHONY: e2e
e2e:  ## run the milestone scenarios against docker-composed stations
	@echo "Not implemented yet — the M1 scenario lands with WP-1.5."
	@echo "  M1 one visit · M2 fan-out and governance · M3 multi-hop · M4 composition"
	@exit 1

.PHONY: up
up:  ## bring up the demo stations
	@echo "Not implemented yet — deploy/compose/ lands with WP-1.4."
	@exit 1

.PHONY: clean
clean:  ## remove the checker virtualenv
	@rm -rf $(VENV)
