"""
Compatibility shim for legacy imports.

Re-exports FastAPI `app` from `src.server.main`.
"""

from src.server.main import app  # noqa: F401

