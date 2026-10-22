"""Bounded UTF-8 JSON input and consistent CLI text streams."""
import json
import os
import stat
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


def is_linked_path(path):
    """Detect one symlink or Windows reparse point without following the link."""
    path = Path(path)
    if path.is_symlink():
        return True
    if os.name == "nt":
        try:
            return bool(os.lstat(path).st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
        except (FileNotFoundError, NotADirectoryError):
            return False
    return False


def private_output_path(destination):
    """Check a private destination before writes; callers keep overwrite semantics."""
    raw = Path(destination).expanduser().absolute()
    if any(is_linked_path(parent) for parent in (raw, *raw.parents)):
        raise ContractError("Output path must not use symlinks or junctions")
    target = raw.resolve()
    installation = Path(__file__).resolve().parents[1]
    if target == installation or installation in target.parents:
        raise ContractError("Private artifacts must live outside the Skill installation")
    if any((parent / ".git").exists() or is_linked_path(parent / ".git")
           for parent in (target, *target.parents)):
        raise ContractError("Private artifacts must live outside Git repositories")
    return target
