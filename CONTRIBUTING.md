# Contributing

Welcome! Please start with a synthetic fixture or a documented mathematical reference. Changes to indicators, fills and bar timing **must** include deterministic regression tests. Review `docs/EXECUTION_AND_SCHEMA.md` before changing order semantics. File issues with expected and observed outputs; do not submit proprietary Pine scripts or account data.

Use `python -m unittest discover -s tests -v` locally. Pull requests should describe input contracts, temporal behavior, actual parity evidence (if claimed), and backward compatibility. No fabricated stars, users or downloads. MIT license.
