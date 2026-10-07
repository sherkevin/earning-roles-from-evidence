"""Bounded prior public transcripts for one actor in one serial stream and arm.

One row is one *completed actor episode per task_index*. A recipient can put
its judgment and action together in actor_response; two stage writes for the
same actor/task are invalid. This is a public-history state container, not a
training algorithm, reflection engine, or role selector.

The forbidden-key check covers structured field names only. It cannot prove
that free-text strings contain no private material. Before recording, the
caller must project task input and actor output through the task's public
allowlist and must persist snapshot() at each decision/read cut. read_before()
reads the current retained suffix, not an arbitrary historical reconstruction.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any, Mapping

SCHEMA = 'peerrolebench-actor-experience-v1'
ENTRY_KEYS = frozenset({'interaction_id', 'task_index', 'task_input', 'actor_response', 'model_metadata'})
META_KEYS = frozenset({'model_id', 'returned_model', 'request_id', 'usage',
                       'elapsed_seconds', 'stop_reason', 'stage'})
FORBIDDEN_KEYS = frozenset({'qp', 'y', 'gold', 'hidden_tests', 'hidden_test',
                            'private_scorer', 'terminal_outcome', 'evaluator_result',
                            'quality_score', 'producer_score'})


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _json_copy(value: Any) -> Any:
    return json.loads(canonical_bytes(value))


def _check_public(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str) or key.lower() in FORBIDDEN_KEYS:
                raise ValueError('interaction contains a private/evaluator field')
            _check_public(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _check_public(item)
    elif value is not None and type(value) not in (str, int, float, bool):
        raise ValueError('interaction must contain JSON values only')
    canonical_bytes(value)


def _entry(*, interaction_id: str, task_index: int, task_input: Any,
           actor_response: Any, model_metadata: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(interaction_id, str) or not interaction_id:
        raise ValueError('interaction_id is required')
    if type(task_index) is not int or task_index < 0:
        raise ValueError('task_index must be a non-negative integer')
    if not isinstance(model_metadata, Mapping) or set(model_metadata) - META_KEYS:
        raise ValueError('model_metadata has unsupported fields')
    if not model_metadata.get('model_id') or not isinstance(model_metadata['model_id'], str):
        raise ValueError('model_metadata.model_id is required')
    if 'usage' in model_metadata:
        usage = model_metadata['usage']
        if (not isinstance(usage, Mapping) or set(usage) != {'input_tokens', 'output_tokens'}
                or any(type(value) is not int or value < 0 for value in usage.values())):
            raise ValueError('model usage must contain non-negative input/output tokens')
    for value in (task_input, actor_response, model_metadata):
        _check_public(value)
    return _json_copy({'interaction_id': interaction_id, 'task_index': task_index,
                       'task_input': task_input, 'actor_response': actor_response,
                       'model_metadata': dict(model_metadata)})


class ActorExperience:
    """One isolated actor store; callers persist and restore each decision snapshot.

    Snapshot hashes detect accidental corruption, not a malicious writer able
    to rewrite both data and digest. Namespace IDs are checked on restore.
    """

    def __init__(self, *, stream_id: str, arm_id: str, actor_id: str,
                 max_entries: int = 2, max_state_bytes: int = 32768):
        if any(not isinstance(value, str) or not value for value in (stream_id, arm_id, actor_id)):
            raise ValueError('stream, arm, and actor IDs are required')
        if type(max_entries) is not int or max_entries < 1:
            raise ValueError('max_entries must be positive')
        if type(max_state_bytes) is not int or max_state_bytes < 1024:
            raise ValueError('max_state_bytes must be at least 1024')
        self.stream_id, self.arm_id, self.actor_id = stream_id, arm_id, actor_id
        self.max_entries, self.max_state_bytes = max_entries, max_state_bytes
        self._entries: list[dict[str, Any]] = []
        self._seen: dict[str, dict[str, Any]] = {}

    def _payload(self) -> dict[str, Any]:
        return {'schema': SCHEMA, 'stream_id': self.stream_id, 'arm_id': self.arm_id,
                'actor_id': self.actor_id, 'max_entries': self.max_entries,
                'max_state_bytes': self.max_state_bytes, 'entries': self._entries,
                'seen': self._seen}

    def snapshot(self) -> dict[str, Any]:
        payload = self._payload()
        return deepcopy({**payload, 'state_digest': digest(payload)})

    def read_before(self, task_index: int) -> list[dict[str, Any]]:
        if type(task_index) is not int or task_index < 0:
            raise ValueError('task_index must be a non-negative integer')
        if self._seen and task_index <= max(item['task_index'] for item in self._seen.values()):
            raise ValueError('read_before requires a future decision; restore its saved snapshot for a past cut')
        return deepcopy([row for row in self._entries if row['task_index'] < task_index])

    def materialize_prompt(self, task_index: int) -> str:
        """Return deterministic prior-transcript JSON; current/future rows are absent."""
        return json.dumps(self.read_before(task_index), sort_keys=True,
                          separators=(',', ':'), ensure_ascii=False)

    def record_completed_interaction(self, *, interaction_id: str, task_index: int,
                                     task_input: Any, actor_response: Any,
                                     model_metadata: Mapping[str, Any]) -> str:
        """Commit one complete public episode atomically after its actor call(s).

        Pass the exact public task input and parsed actor response. For a
        recipient, actor_response may contain both judgment and action. Map
        model metadata into the supported fields; do not include evaluator
        Qp/Y, private tests, or another actor's transcript.
        """
        row = _entry(interaction_id=interaction_id, task_index=task_index,
                     task_input=task_input, actor_response=actor_response,
                     model_metadata=model_metadata)
        row_digest = digest(row)
        prior = self._seen.get(interaction_id)
        if prior is not None:
            if prior != {'task_index': task_index, 'entry_digest': row_digest}:
                raise ValueError('conflicting duplicate interaction_id')
            return row_digest
        if self._seen and task_index <= max(item['task_index'] for item in self._seen.values()):
            raise ValueError('task indexes must increase strictly')
        entries = [*self._entries, row][-self.max_entries:]
        seen = {**self._seen, interaction_id: {'task_index': task_index, 'entry_digest': row_digest}}
        candidate = {**self._payload(), 'entries': entries, 'seen': seen}
        if len(canonical_bytes(candidate)) > self.max_state_bytes:
            raise ValueError('actor experience byte cap exceeded')
        self._entries, self._seen = entries, seen
        return row_digest

    @classmethod
    def restore(cls, snapshot: Mapping[str, Any], *, stream_id: str, arm_id: str,
                actor_id: str) -> 'ActorExperience':
        expected = {'schema', 'stream_id', 'arm_id', 'actor_id', 'max_entries',
                    'max_state_bytes', 'entries', 'seen', 'state_digest'}
        if not isinstance(snapshot, Mapping) or set(snapshot) != expected or snapshot['schema'] != SCHEMA:
            raise ValueError('unsupported actor experience snapshot')
        if (snapshot['stream_id'], snapshot['arm_id'], snapshot['actor_id']) != (stream_id, arm_id, actor_id):
            raise ValueError('actor experience namespace mismatch')
        payload = {key: snapshot[key] for key in expected - {'state_digest'}}
        if digest(payload) != snapshot['state_digest']:
            raise ValueError('actor experience snapshot hash mismatch')
        store = cls(stream_id=stream_id, arm_id=arm_id, actor_id=actor_id,
                    max_entries=snapshot['max_entries'], max_state_bytes=snapshot['max_state_bytes'])
        entries, seen = snapshot['entries'], snapshot['seen']
        if not isinstance(entries, list) or len(entries) > store.max_entries or not isinstance(seen, Mapping):
            raise ValueError('actor experience snapshot inventory invalid')
        rebuilt = []
        previous = -1
        for raw in entries:
            if not isinstance(raw, Mapping) or set(raw) != ENTRY_KEYS:
                raise ValueError('actor experience entry schema invalid')
            row = _entry(**raw)
            if row['task_index'] <= previous:
                raise ValueError('actor experience order invalid')
            previous = row['task_index']
            if seen.get(row['interaction_id']) != {'task_index': row['task_index'], 'entry_digest': digest(row)}:
                raise ValueError('actor experience entry index mismatch')
            rebuilt.append(row)
        for key, value in seen.items():
            if (not isinstance(key, str) or not key or not isinstance(value, Mapping)
                    or set(value) != {'task_index', 'entry_digest'}
                    or type(value['task_index']) is not int or value['task_index'] < 0
                    or not isinstance(value['entry_digest'], str) or len(value['entry_digest']) != 64):
                raise ValueError('actor experience seen index invalid')
        indexes = [item['task_index'] for item in seen.values()]
        if len(set(indexes)) != len(indexes):
            raise ValueError('actor experience duplicate task index')
        suffix = [key for key, _ in sorted(seen.items(), key=lambda pair: pair[1]['task_index'])][-store.max_entries:]
        if [row['interaction_id'] for row in rebuilt] != suffix:
            raise ValueError('actor experience retained suffix invalid')
        if rebuilt and max(item['task_index'] for item in seen.values()) != rebuilt[-1]['task_index']:
            raise ValueError('actor experience suffix invalid')
        store._entries, store._seen = rebuilt, deepcopy(dict(seen))
        if len(canonical_bytes(store._payload())) > store.max_state_bytes:
            raise ValueError('actor experience byte cap exceeded')
        return store


__all__ = ['ActorExperience', 'SCHEMA', 'canonical_bytes', 'digest']
