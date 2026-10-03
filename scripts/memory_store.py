"""Bounded, local SQLite memory with explicit consent and read/write gates."""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.models import ContractError, audit_claim, choices, items, obj, text

POLICY_VERSION = "1"
MAX_RECORDS = 200
LIMITS = {"profile": 10, "target_role": 10, "project": 25, "claim": 40, "company": 20,
          "application": 40, "interview_event": 30, "feedback": 30, "decision": 30, "outcome": 30}
STATES = {"active", "paused", "revoked"}
IMMUTABLE = {"decision", "outcome"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def default_directory() -> Path:
    if os.environ.get("CAREER_JUNSHI_MEMORY_DIR"):
        return Path(os.environ["CAREER_JUNSHI_MEMORY_DIR"]).expanduser()
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "career-junshi"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "career-junshi"
    return Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))) / "career-junshi"


class MemoryStore:
    def __init__(self, directory: str | Path | None = None):
        self.directory = Path(directory).expanduser().resolve() if directory is not None else default_directory().resolve()
        installation = Path(__file__).resolve().parents[1]
        if self.directory == installation or installation in self.directory.parents:
            raise ContractError("Memory must be outside the Skill installation / public repository")
        self.path = self.directory / "memory.sqlite3"

    @contextmanager
    def connection(self, *, create=False, write=False):
        if not self.path.exists() and not create:
            raise ContractError("Memory is not initialized; explicit consent is required")
        if create:
            self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        uri = self.path.as_uri() + "?mode=" + ("rwc" if create else "rw" if write else "ro")
        conn = sqlite3.connect(uri, uri=True, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            if write or create:
                conn.execute("BEGIN IMMEDIATE")
            yield conn
            if write or create:
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def status(self) -> dict:
        if not self.path.exists():
            return {"state": "uninitialized", "records": 0, "policy_version": POLICY_VERSION}
        with self.connection() as c:
            state = self._state(c)
            return {"state": state, "records": c.execute("SELECT COUNT(*) FROM records").fetchone()[0], "policy_version": POLICY_VERSION}

    @staticmethod
    def _state(c) -> str:
        meta = dict(c.execute("SELECT key, value FROM settings").fetchall())
        if meta.get("policy_version") != POLICY_VERSION:
            raise ContractError("Memory policy changed; migration and renewed consent required")
        return choices(meta.get("state"), STATES, "memory state")

    def _active(self, c):
        if self._state(c) != "active":
            raise ContractError("Memory paused or revoked: recall / writes disabled; view / delete remain available")

    def consent(self, *, confirmed: bool = False) -> dict:
        if confirmed is not True:
            raise ContractError("Explicit consent required; do not infer consent from use")
        with self.connection(create=True, write=True) as c:
            c.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
            existing = dict(c.execute("SELECT key,value FROM settings").fetchall())
            if existing and existing.get("policy_version") != POLICY_VERSION:
                raise ContractError("Unsupported memory version; do not overwrite consent")
            c.execute("""CREATE TABLE IF NOT EXISTS records (
                id TEXT PRIMARY KEY, kind TEXT NOT NULL, subject TEXT NOT NULL,
                data TEXT NOT NULL, parent_id TEXT REFERENCES records(id) ON DELETE CASCADE,
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL)""")
            c.execute("CREATE INDEX IF NOT EXISTS by_subject ON records(subject,kind,updated_at)")
            for key, value in (("policy_version", POLICY_VERSION), ("state", "active"), ("consented_at", now_iso())):
                c.execute("INSERT OR REPLACE INTO settings VALUES (?,?)", (key, value))
        return self.status()

    def set_state(self, state: str) -> dict:
        choices(state, {"paused", "revoked"}, "state")
        with self.connection(write=True) as c:
            current = self._state(c)
            if current == "revoked" and state == "paused":
                raise ContractError("Revocation cannot be weakened without renewed explicit consent")
            c.execute("UPDATE settings SET value=? WHERE key='state'", (state,))
        return self.status()

    @staticmethod
    def _base(data: dict) -> dict:
        d = obj(data, "memory data")
        return {"summary": text(d.get("summary"), "summary", 400),
                "source": text(d.get("source"), "source", 240),
                "epistemic": choices(d.get("epistemic"), {"FACT", "INFERENCE", "UNKNOWN"}, "epistemic")}

    @classmethod
    def normalize_record(cls, kind: str, data: dict) -> dict:
        choices(kind, set(LIMITS), "memory kind")
        d = obj(data, "data")
        if kind == "claim":
            if set(d) != {"summary", "source", "epistemic", "claim"}:
                raise ContractError("claim memory requires compact provenance and the raw claim model")
            base = cls._base(d)
            audited = audit_claim(d["claim"])
            # Retain normalized narrow claim, never a claimed verification level.
            base["claim"] = audited
            base["summary"] = audited["safe_wording"][:400]
            base["epistemic"] = "FACT" if audited["confidence"] == "VERIFIED" else "INFERENCE" if audited["confidence"] == "PLANNED" else "UNKNOWN"
            return base
        if kind in IMMUTABLE:
            raise ContractError("Use record_decision / record_outcome for immutable history")
        if set(d) != {"summary", "source", "epistemic"}:
            raise ContractError("Memory accepts compact fields only; no raw resume / JD / email / chat")
        return cls._base(d)

    def _put(self, kind: str, subject: str, data: dict, *, record_id=None, parent_id=None) -> dict:
        subject = text(subject, "subject", 100)
        record_id = text(record_id, "record_id", 80) if record_id is not None else uuid.uuid4().hex
        serialized = json.dumps(data, ensure_ascii=False, allow_nan=False)
        if len(serialized) > 6000:
            raise ContractError("Record exceeds compact memory budget (6000 characters)")
        with self.connection(write=True) as c:
            self._active(c)
            previous = c.execute("SELECT * FROM records WHERE id=?", (record_id,)).fetchone()
            if previous:
                if previous["kind"] != kind or previous["subject"] != subject:
                    raise ContractError("Cannot change record kind or subject by update")
                if kind in IMMUTABLE:
                    raise ContractError("Decision / Outcome history is append-only")
            else:
                if c.execute("SELECT COUNT(*) FROM records").fetchone()[0] >= MAX_RECORDS:
                    raise ContractError("Memory full; explicitly delete obsolete records, do not silently evict history")
                if c.execute("SELECT COUNT(*) FROM records WHERE kind=?", (kind,)).fetchone()[0] >= LIMITS[kind]:
                    raise ContractError(f"Memory limit for {kind}; review and delete obsolete records")
            if parent_id:
                parent = c.execute("SELECT kind,subject FROM records WHERE id=?", (parent_id,)).fetchone()
                if not parent or parent["kind"] != "decision" or parent["subject"] != subject:
                    raise ContractError("Outcome must reference a Decision for the same subject")
            stamp = now_iso()
            c.execute("""INSERT INTO records VALUES (?,?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET data=excluded.data,updated_at=excluded.updated_at""",
                (record_id, kind, subject, serialized, parent_id, previous["created_at"] if previous else stamp, stamp))
        return {"id": record_id, "kind": kind, "subject": subject, "saved": True}

    def put(self, kind: str, subject: str, data: dict, *, record_id=None) -> dict:
        return self._put(kind, subject, self.normalize_record(kind, data), record_id=record_id)

    def record_decision(self, subject: str, data: dict) -> dict:
        d = obj(data, "decision memory")
        required = {"situation", "decision", "why", "expected_outcome", "source", "observation_window", "stop_condition", "pivot_condition"}
        if set(d) != required:
            raise ContractError(f"Decision memory fields must be {sorted(required)}")
        clean = {k: text(d[k], k, 600 if k in {"decision", "why"} else 400) for k in required}
        clean["epistemic"] = "INFERENCE"
        return self._put("decision", subject, clean)

    def record_outcome(self, subject: str, data: dict) -> dict:
        d = obj(data, "outcome memory")
        required = {"decision_id", "hard_outcome", "observed_facts", "user_interpretation", "agent_interpretation", "unknowns", "source"}
        if set(d) != required:
            raise ContractError(f"Outcome memory fields must be {sorted(required)}")
        parent = text(d["decision_id"], "decision_id", 80)
        outcome = choices(d["hard_outcome"], {"passed", "rejected", "offer", "waiting", "withdrawn", "freeze", "unknown"}, "hard_outcome")
        facts = []
        for raw in items(d["observed_facts"], "observed_facts", 5):
            raw = obj(raw, "observed fact")
            if set(raw) != {"text", "source"}:
                raise ContractError("observed facts need exact text and source")
            facts.append({"text": text(raw["text"], "fact", 240), "source": text(raw["source"], "source", 240)})
        clean = {"decision_id": parent, "hard_outcome": outcome, "observed_facts": facts,
                 "user_interpretation": text(d["user_interpretation"], "user_interpretation", 400, empty=True),
                 "agent_interpretation": text(d["agent_interpretation"], "agent_interpretation", 400, empty=True),
                 "unknowns": [text(u, "unknown", 240) for u in items(d["unknowns"], "unknowns", 5)],
                 "source": text(d["source"], "source", 240), "epistemic": "FACT"}
        # The engine creates a bounded learning, never promotes interpretations to facts.
        clean["learning"] = "本次观察已记录；仅适用于本次机会，不证明准备策略导致结果。"
        clean["unknowns"] = list(dict.fromkeys(clean["unknowns"] + ["结果的因果原因与策略效果仍未知"]))
        if not facts:
            clean["unknowns"].append("缺少具体观察，无法判断哪项准备相关")
        return self._put("outcome", subject, clean, parent_id=parent)

    def read(self, *, kind=None, subject=None, administrative=False, limit=10) -> list:
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_RECORDS:
            raise ContractError(f"limit must be 1..{MAX_RECORDS}")
        with self.connection() as c:
            if administrative:
                self._state(c)
            else:
                self._active(c)
                if not kind and not subject:
                    raise ContractError("Recall needs a task-relevant kind or subject")
            query = "SELECT * FROM records WHERE 1=1"
            args = []
            if kind:
                choices(kind, set(LIMITS), "kind")
                query += " AND kind=?"; args.append(kind)
            if subject:
                query += " AND subject=?"; args.append(text(subject, "subject", 100))
            query += " ORDER BY updated_at DESC,id LIMIT ?"; args.append(limit)
            rows = c.execute(query, args).fetchall()
            return [{**dict(row), "data": json.loads(row["data"])} for row in rows]

    def delete(self, record_id: str | None = None, *, confirmed=False) -> dict:
        if confirmed is not True:
            raise ContractError("Deletion requires explicit confirmation")
        if not self.path.exists():
            return {"deleted": 0, "state": "uninitialized"}
        with self.connection(write=True) as c:
            self._state(c)
            before = c.execute("SELECT COUNT(*) FROM records").fetchone()[0]
            if record_id is not None:
                c.execute("DELETE FROM records WHERE id=?", (text(record_id, "record_id", 80),))
            else:
                c.execute("DELETE FROM records")
                c.execute("UPDATE settings SET value='revoked' WHERE key='state'")
            after = c.execute("SELECT COUNT(*) FROM records").fetchone()[0]
        # Compact freed pages. This is logical deletion, not forensic erasure / backup deletion.
        with self.connection(write=True) as c:
            c.commit()
            c.execute("VACUUM")
        return {"deleted": before - after, "state": self.status()["state"], "boundary": "Logical deletion only; external copies/backups are not erased."}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--directory", help="Private directory outside the Skill installation")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    for name in ("consent", "delete"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--yes", action="store_true", help="Only after explicit user consent / deletion request")
        if name == "delete":
            cmd.add_argument("--id")
    sub.add_parser("pause"); sub.add_parser("revoke")
    for name in ("view", "recall"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--kind", choices=sorted(LIMITS)); cmd.add_argument("--subject")
        cmd.add_argument("--limit", type=int, default=10)
    for name in ("update", "decision", "outcome"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--subject", required=True); cmd.add_argument("--input", required=True)
        if name == "update":
            cmd.add_argument("--kind", required=True, choices=sorted(LIMITS))
            cmd.add_argument("--id")
    args = p.parse_args(argv)
    try:
        store = MemoryStore(args.directory)
        if args.command == "status":
            result = store.status()
        elif args.command == "consent":
            result = store.consent(confirmed=args.yes)
        elif args.command in {"pause", "revoke"}:
            result = store.set_state("paused" if args.command == "pause" else "revoked")
        elif args.command == "delete":
            result = store.delete(args.id, confirmed=args.yes)
        elif args.command in {"view", "recall"}:
            result = store.read(kind=args.kind, subject=args.subject, limit=args.limit, administrative=args.command == "view")
        else:
            data = json.loads(Path(args.input).read_text(encoding="utf-8"))
            if args.command == "update":
                result = store.put(args.kind, args.subject, data, record_id=args.id)
            elif args.command == "decision":
                result = store.record_decision(args.subject, data)
            else:
                result = store.record_outcome(args.subject, data)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (ContractError, OSError, sqlite3.Error, ValueError) as exc:
        print(json.dumps({"error": str(exc), "saved": False}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
