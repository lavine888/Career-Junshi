"""Bounded UTF-8 JSON input and consistent CLI text streams."""
import json
import sys
from pathlib import Path

from scripts.models import ContractError


def load_json_input(path):
    source = Path(path)
    if source.stat().st_size > 256 * 1024:
        raise ContractError("Structured input must be <= 256 KiB; extract compact context first")
    return json.loads(source.read_text(encoding="utf-8-sig"))


def configure_cli_streams():
    for stream in (sys.stdout, sys.stderr):
        if callable(getattr(stream, "reconfigure", None)):
            stream.reconfigure(encoding="utf-8")
