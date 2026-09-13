"""Reading a testbed profile.

A profile is a `KEY=value` file, and the values are not shell. `FDT_STATION_DATASETS` is a JSON
array and `FDT_STATION_TITLE` contains a space and an em dash; `set -a; . profile.env` mangles
both, which is how the first attempt at this failed. So the runner parses the file itself and
hands the result to the subprocess as its environment, where no shell ever sees it.

Deliberately not a `.env` library: the rules are four lines, and the one thing that matters is
that a value is taken **verbatim** to the end of the line. Stripping quotes, expanding `$VAR` or
honouring `#` mid-line would each silently change a configured IRI into a different one.
"""

from __future__ import annotations

from pathlib import Path

__all__ = ["read_profile"]


def read_profile(path: Path) -> dict[str, str]:
    """`KEY=value` pairs. Blank lines and whole-line `#` comments are skipped."""
    values: dict[str, str] = {}
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        if not separator:
            raise ValueError(f"{path}:{number}: not a KEY=value line: {raw!r}")
        key = key.strip()
        if not key:
            raise ValueError(f"{path}:{number}: empty key")
        # Not `.strip()` on the value beyond the ends: a trailing space is almost certainly a
        # typo, and a leading one certainly is, but anything inside belongs to the value.
        values[key] = value.strip()
    return values
