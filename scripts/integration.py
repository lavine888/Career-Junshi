"""Explicit snapshot reader; no Vault discovery, authentication or persistence."""
from __future__ import annotations

import json
import re

from scripts.context import extract, freshness as check_freshness
from scripts.io_utils import private_output_path
from scripts.models import ContractError, choices, items, obj, text, timestamp

TYPES = {'Profile', 'Project', 'Claim', 'Company', 'Person', 'Opportunity', 'Application',
         'Interview', 'Feedback', 'Event', 'Situation', 'Decision', 'Outcome', 'Evidence', 'Source', 'Knowledge'}


def adapt_snapshot(value, *, mode='job', now=None):
    snapshot = obj(value, 'career snapshot')
    allowed = {'schema_version', 'context_id', 'purpose', 'records', 'privacy', 'generated_at', 'as_of', 'depth', 'unknowns'}
    if set(snapshot) - allowed or snapshot.get('schema_version') != '1':
        raise ContractError('career snapshot v1 required; unsupported fields rejected')
    text(snapshot.get('context_id'), 'context ID', 100)
    purpose = text(snapshot.get('purpose'), 'purpose', 400)
    if snapshot.get('privacy', 'local-only') != 'local-only':
        raise ContractError('snapshot must be local-only')
    mode = choices(mode, {'job', 'interview', 'positioning', 'offer', 'recruiting'}, 'mode')
    sources, statements = [], []
    ids = set()
    for raw in items(snapshot.get('records'), 'snapshot records', 11):
        r = obj(raw, 'snapshot record')
        permitted = {'id', 'type', 'summary', 'source_ref', 'source_fingerprint', 'observed_at',
                     'last_updated', 'freshness', 'epistemic', 'confidence', 'ownership', 'level'}
        required = {'id', 'type', 'summary', 'source_ref', 'source_fingerprint', 'observed_at', 'epistemic', 'confidence', 'ownership'}
        if set(r) - permitted or not required <= r.keys():
            raise ContractError('invalid snapshot record fields')
        sid = text(r['id'], 'record ID', 80)
        if sid in ids:
            raise ContractError('duplicate snapshot record ID')
        ids.add(sid)
        kind = choices(r['type'], TYPES, 'record type')
        summary = text(r['summary'], 'record summary', 400)
        text(r['source_ref'], 'source reference', 240)
        text(r['ownership'], 'reported ownership', 400)
        if not re.fullmatch(r'[0-9a-f]{64}', str(r['source_fingerprint'])):
            raise ContractError('source fingerprint must be a local SHA256; not proof of truth')
        if r['observed_at'] != 'unknown':
            timestamp(r['observed_at'], 'observed_at')
        confidence = choices(r['confidence'], {'VERIFIED', 'SUPPORTED', 'SELF_REPORTED', 'PLANNED'}, 'reported confidence')
        epistemic = choices(r['epistemic'], {'FACT', 'INFERENCE', 'UNKNOWN'}, 'epistemic')
        freshness = choices(r.get('freshness', 'UNKNOWN'), {'CURRENT', 'STALE', 'UNKNOWN'}, 'freshness')
        if kind in {'Opportunity', 'Company', 'Application', 'Interview', 'Source'}:
            dates = {'category': 'current_jd'}
            if r['observed_at'] != 'unknown':
                dates['observed_at'] = r['observed_at']
            checked = check_freshness(dates, now=now)['status']
            if checked != 'CURRENT_SOURCE':
                freshness = 'STALE' if checked == 'STALE' else 'UNKNOWN'
        # Preserve the original labels in session source text. They are claims by
        # the source, not newly authenticated evidence or structured Claim receipts.
        sources.append({'source_id': sid, 'source_type': 'user_report',
                        'text': summary + '\n' + json.dumps(r, ensure_ascii=False, separators=(',', ':'))})
        if confidence == 'PLANNED' or freshness != 'CURRENT':
            epistemic = 'UNKNOWN'
        if re.search(r'感觉|可能|似乎|\b(?:feel|maybe|seems)\b', summary, re.I) and epistemic == 'FACT':
            epistemic = 'INFERENCE'
        if kind in {'Decision', 'Outcome', 'Evidence', 'Source', 'Knowledge'} and epistemic == 'FACT':
            epistemic = 'UNKNOWN'
        statement_text = summary if epistemic != 'UNKNOWN' or len(summary) <= 240 else f'{sid}: unresolved source; inspect the supplied record before treating it as current fact.'
        statements.append({'id': 'record-' + str(len(statements)+1), 'text': statement_text,
                           'source_id': sid, 'source_type': 'user_report', 'source_span': summary,
                           'epistemic': epistemic,
                           'confidence': 'interpretation' if epistemic == 'INFERENCE' else 'unknown' if epistemic == 'UNKNOWN' else 'self_reported',
                           'kind': 'claim' if kind == 'Claim' else 'observation', 'modality': 'unknown' if epistemic == 'UNKNOWN' else 'observed'})
    gaps = [text(gap, 'snapshot gap', 240) for gap in items(snapshot.get('unknowns', []), 'snapshot gaps', 30)]
    if len(gaps) > 30 - len(statements):
        raise ContractError('snapshot gaps exceed extraction statement budget; narrow context')
    if gaps:
        if 'snapshot-gaps' in ids:
            raise ContractError('reserved snapshot ID')
        sources.append({'source_id': 'snapshot-gaps', 'source_type': 'tool', 'text': '\n'.join(gaps)})
        for index, gap in enumerate(gaps):
            statements.append({'id': f'gap-{index+1}', 'text': gap, 'source_id': 'snapshot-gaps',
                               'source_type': 'tool', 'source_span': gap, 'epistemic': 'UNKNOWN',
                               'confidence': 'unknown', 'kind': 'observation', 'modality': 'unknown'})
    packet = {'schema_version': '1', 'sources': sources, 'statements': statements,
              'situation': {'mode': mode, 'summary': purpose, 'goal': purpose, 'claims': []}}
    extract(packet, now=now)  # Reuse the existing contract; never add a new decision schema.
    return packet


def write_private_packet(packet, destination):
    path = private_output_path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(packet, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    return path
