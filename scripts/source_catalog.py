"""Bounded offline source discovery; catalog metadata is not live verification."""
from __future__ import annotations

import copy
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

from scripts.models import ContractError

ROOT = Path(__file__).resolve().parents[1]
CATALOG_FILES = (
    "references/research/search-and-choice.json",
    "references/research/interview-and-practice.json",
    "references/research/offer-rights-and-safety.json",
)
TOPICS = {"job_search", "career_choice", "resume", "interview",
          "negotiation", "offer", "rights", "safety"}
KINDS = {"meta_analysis", "experiment", "theory", "review",
         "practice_guide", "official_guidance", "legislation"}
DEPTHS = {"abstract", "selected_sections", "full_text", "official_page", "bibliographic_record"}
FIELDS = {"id", "title", "authors", "year", "kind", "topics", "url", "checked_on",
          "read_depth", "setting", "finding", "use", "limits", "jurisdiction", "version"}
SUMMARY = ("id", "title", "kind", "topics", "url", "checked_on", "read_depth")


def _string(value, field, maximum=2000):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ContractError(f"source {field} must be nonempty text <= {maximum} characters")


def validate_catalog(records):
    """Validate source identity and scope metadata, never authenticate findings."""
    if not isinstance(records, list) or not 1 <= len(records) <= 250:
        raise ContractError("source catalog must contain 1..250 distinct records")
    ids, urls, titles = set(), set(), set()
    for record in records:
        if not isinstance(record, dict) or set(record) != FIELDS:
            raise ContractError("source record has missing or unknown fields")
        for field in FIELDS - {"topics", "limits"}:
            _string(record[field], field)
        if not re.fullmatch(r"R[1-9][0-9]{0,3}", record["id"]):
            raise ContractError("source ID must use R followed by a positive number")
        if record["id"] in ids:
            raise ContractError("duplicate source ID")
        ids.add(record["id"])
        address = urlsplit(record["url"])
        if address.scheme != "https" or not address.hostname or address.username or address.password:
            raise ContractError("source URL must be public HTTPS without credentials")
        if address.hostname in {"localhost", "127.0.0.1", "::1"}:
            raise ContractError("source URL cannot be localhost")
        identity = record["url"].split("#")[0].rstrip("/")
        title = " ".join(record["title"].casefold().split())
        if identity in urls or title in titles:
            raise ContractError("duplicate source work or canonical URL")
        urls.add(identity)
        titles.add(title)
        try:
            date.fromisoformat(record["checked_on"])
        except ValueError as exc:
            raise ContractError("source checked_on must be an ISO date") from exc
        if record["kind"] not in KINDS or record["read_depth"] not in DEPTHS:
            raise ContractError("unsupported source kind or reading depth")
        topics = record["topics"]
        if (not isinstance(topics, list) or not topics or len(topics) > len(TOPICS)
                or any(not isinstance(topic, str) or topic not in TOPICS for topic in topics)
                or len(set(topics)) != len(topics)):
            raise ContractError("source topics must be distinct supported topics")
        limits = record["limits"]
        if not isinstance(limits, list) or not 1 <= len(limits) <= 8:
            raise ContractError("source must state 1..8 transfer or access limits")
        for limit in limits:
            _string(limit, "limit", 1000)
    return copy.deepcopy(sorted(records, key=lambda record: int(record["id"][1:])))


def load_catalog(root=ROOT):
    records = []
    for name in CATALOG_FILES:
        path = Path(root) / name
        if not path.is_file() or path.is_symlink() or path.stat().st_size > 256 * 1024:
            raise ContractError("missing, linked or oversized catalog: " + name)
        try:
            packet = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, UnicodeError) as exc:
            raise ContractError("invalid source catalog JSON: " + name) from exc
        if (not isinstance(packet, dict) or set(packet) != {"schema_version", "sources"}
                or packet["schema_version"] != "1" or not isinstance(packet["sources"], list)):
            raise ContractError("source catalog requires schema_version 1 and sources")
        records.extend(packet["sources"])
    return validate_catalog(records)


def query_sources(*, topic=None, source_id=None, limit=3, root=ROOT):
    if type(limit) is not int or not 1 <= limit <= 10:
        raise ContractError("source limit must be 1..10")
    if topic is not None and source_id is not None:
        raise ContractError("select a topic or source ID, not both")
    if topic is not None and (not isinstance(topic, str) or topic not in TOPICS):
        raise ContractError("unknown source topic")
    records = load_catalog(root)
    selected = records
    if source_id is not None:
        if not isinstance(source_id, str):
            raise ContractError("source ID must be text")
        selected = [record for record in records if record["id"] == source_id]
        if not selected:
            raise ContractError("unknown source ID")
    elif topic is not None:
        selected = [record for record in records if topic in record["topics"]]
    shown = selected[:limit]
    if source_id is None:
        shown = [{key: record[key] for key in SUMMARY} for record in shown]
    return {
        "schema_version": "1",
        "total_sources": len(records),
        "topic_counts": dict(sorted(Counter(topic for record in records for topic in record["topics"]).items())),
        "kind_counts": dict(sorted(Counter(record["kind"] for record in records).items())),
        "matched_sources": len(selected),
        "returned_sources": len(shown),
        "sources": shown,
        "detail": source_id is not None,
        "boundary": "Offline curated metadata; catalog order is not an evidence ranking. "
                    "No live source, legal status, candidate claim or product effect is verified by this command.",
    }
