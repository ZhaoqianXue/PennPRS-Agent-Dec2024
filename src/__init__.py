"""
Compatibility package.

Historically this repository used a `src.*` Python import layout (e.g. `src.main`,
`src.core.*`, `src.modules.*`). The backend has since been reorganized under
`src.server.*`, but some tests (and external scripts) still import from `src.*`.

This package provides lightweight shims that re-export the current backend modules.
"""

