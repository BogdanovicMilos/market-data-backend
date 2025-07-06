from __future__ import annotations

import os
import pathlib
import typing as _t
import yaml


MODULE_DIR = pathlib.Path(__file__).resolve().parent
DEFAULT_FILE = MODULE_DIR / "ingestion_config.yaml"
FILE = pathlib.Path(os.getenv("CONFIG_PATH", DEFAULT_FILE))


def load_symbols(overrides: _t.Mapping[str, _t.Any] | None = None) -> dict:
    base: dict = {}
    if FILE.exists():
        base = yaml.safe_load(FILE.read_text()) or {}
    if overrides:
        base.update(overrides)
    return base
