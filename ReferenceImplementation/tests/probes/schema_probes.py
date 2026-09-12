import json, os
from jsonschema import Draft202012Validator, FormatChecker
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); S = os.path.join(ROOT, "fdt-commons/schemas")
ev = json.load(open(os.path.join(S, "visit-event.schema.json"))); res = json.load(open(os.path.join(S, "visit-result.schema.json")))
def run(schema, inst, label):
    errs = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(inst))
    print(f"[{'VALID' if not errs else 'invalid'}] {label}"); [print("     -", e.message[:140]) for e in errs]
base = {"id": "https://s.example/e/1", "visit": "https://example.org/fdt/visit/x", "sequence": 1, "time": "2026-09-11T10:00:00Z"}
run(ev, {**base, "type": "negotiation.refused", "state": "Refused"}, "negotiation.refused with NO reason and NO justification")
run(ev, {**base, "type": "negotiation.active", "state": "Queued"}, "negotiation.active with NO agreement, NO justification (who approved?)")
run(ev, {**base, "type": "visit.delivered", "state": "Delivered"}, "visit.delivered with NO justification")
run(ev, {**base, "type": "visit.rejected", "state": "Delivered", "checkpoint": "OBL"}, "visit.rejected carrying state Delivered at checkpoint OBL (type/state/checkpoint not cross-constrained)")
run(res, {"visit": "https://example.org/fdt/visit/x", "station": "https://example.org/fdt/station/s", "hop": 1, "phase": 1, "train": "https://example.org/fdt/train/t", "state": "delivered",
          "result": {"patient_id": "12345", "name": "J. Jansen", "dob": "1961-03-04"}}, "delivered envelope with NO agreement, NO inspection block, record-level fields in result")
run(res, {"visit": "https://example.org/fdt/visit/x", "station": "https://example.org/fdt/station/s", "hop": 1, "phase": 1, "train": "https://example.org/fdt/train/t", "state": "refused", "result": {}}, "refused envelope with NO reason")
