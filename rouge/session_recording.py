"""Opt-in local Gate 0 recording; standard-library queued JSONL, no images."""
from copy import deepcopy
from datetime import datetime, timezone
import json
import logging
from logging.handlers import QueueHandler, QueueListener
from pathlib import Path
from queue import SimpleQueue
import time
from weakref import WeakKeyDictionary


def state_snapshot(state):
    """Explicit game fields only; never notes, chat, credentials or raw OCR."""
    return {
        'run_id': state['id'],
        'config': {key: {k: v for k, v in record.items()
                        if k in ('id', 'name', 'value', 'level', 'modeDifficulty', 'captured_at')}
                   for key, record in state.get('config', {}).items() if isinstance(record, dict)},
        'resources': {key: {k: v for k, v in record.items() if k in ('value', 'captured_at', 'source')}
                      for key, record in state.get('resources', {}).items()},
        'operators': {key: {k: deepcopy(v) for k, v in record.items()
                           if k in ('present', 'fields', 'skill_ranks', 'field_times', 'char_buff_ids')}
                      for key, record in state.get('operators', {}).items()},
        'relics': {key: {k: v for k, v in record.items() if k in ('held', 'count', 'captured_at')}
                   for key, record in state.get('relics', {}).items()},
        'tactical_tools': {key: {k: v for k, v in record.items() if k in ('held', 'count', 'captured_at')}
                          for key, record in state.get('tactical_tools', {}).items()},
    }


class SessionRecorder:
    def __init__(self, folder, *, scenario, clock=time.perf_counter):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=False)
        self.clock = clock
        self.started = clock()
        self.closed = False
        self.previous_state = {}
        self.last_overlay = None
        self.last_overlay_at = float('-inf')
        self.last_surfaces = None
        self.surface_ids = WeakKeyDictionary()
        self.queue = SimpleQueue()
        self.handler = logging.FileHandler(self.folder / 'events.jsonl', mode='x', encoding='utf8')
        self.handler.setFormatter(logging.Formatter('%(message)s'))
        self.listener = QueueListener(self.queue, self.handler)
        self.logger = logging.Logger('gate0-local', level=logging.INFO)
        self.logger.addHandler(QueueHandler(self.queue))
        self.listener.start()
        self.event('session_start', scenario=scenario, utc=datetime.now(timezone.utc).isoformat(),
                   schema='gate0_local_v1', private=True, raw_images=False, raw_ocr=False)

    def event(self, event_type, **data):
        if self.closed:
            return
        self.logger.info(json.dumps({'event': event_type, 't_ms': round((self.clock()-self.started)*1000, 3),
                                     **data}, ensure_ascii=False, separators=(',', ':')))

    def sample(self, observation, state, *, applied, reason, ui_ms=0):
        snapshot = state_snapshot(state)
        diff = {key: value for key, value in snapshot.items() if self.previous_state.get(key) != value}
        self.previous_state = snapshot
        graph = observation.get('map') or {}
        stage = observation.get('stage') or {}
        performance = observation.get('performance', {})
        timing = {k: deepcopy(v) for k, v in performance.items()
                  if k in ('total_ms', 'stages_ms', 'backend', 'reuse')}
        timing['routing'] = {k: v for k, v in performance.get('routing', {}).items()
                            if k in ('page', 'strategy', 'fallback_reason', 'feature_reuse', 'visual_ms', 'score')}
        self.event('sample', page=observation.get('page'), sampling=observation.get('_sampling'),
                   captured_at=observation.get('captured_at'), applied=applied, reason=reason,
                   state_diff=diff, stage_id=stage.get('visible_variant_id') or stage.get('id'),
                   map={'zone_id': graph.get('zone_id'), 'template_id': graph.get('template_id'),
                        'status': graph.get('status')},
                   performance=timing,
                   capture_ms=observation.get('capture_ms'), ui_ms=ui_ms)

    def overlay(self, decision, *, did_show, enabled, kind, now=None):
        current = self.clock() if now is None else now
        row = {**decision, 'did_show': did_show, 'enabled': enabled, 'kind': kind,
               'would_show': None}
        identity = {k: v for k, v in row.items() if k not in ('reference_age_s', 'current_age_s', 'evaluation_ms')}
        if identity != self.last_overlay or current-self.last_overlay_at >= 1:
            self.event('overlay', **row)
            self.last_overlay = identity
            self.last_overlay_at = current

    def surfaces(self, app, *, entry):
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QStackedWidget
        rows = []
        for widget in app.topLevelWidgets():
            if not widget.isVisible():
                continue
            if widget not in self.surface_ids:
                self.surface_ids[widget] = len(self.surface_ids)+1
            parent = widget.parentWidget()
            stack = next((child for child in widget.children() if isinstance(child, QStackedWidget)), None)
            page = stack.currentWidget() if stack else None
            rows.append({'id': self.surface_ids[widget], 'class': type(widget).__name__,
                         'owner_class': type(parent).__name__ if parent else None,
                         'page_class': type(page).__name__ if page else None,
                         'role': widget.property('playerVisibility'),
                         'geometry': list(widget.geometry().getRect()),
                         'dpi_ratio': widget.devicePixelRatioF(),
                         'accepts_focus': not bool(widget.windowFlags() & Qt.WindowType.WindowDoesNotAcceptFocus)})
        rows.sort(key=lambda row: row['id'])
        current = {'entry': entry, 'visible': rows}
        if current != self.last_surfaces:
            self.event('surfaces', **current)
            self.last_surfaces = current

    def close(self):
        if not self.closed:
            self.event('session_end')
            self.closed = True
            self.listener.stop()
            self.handler.close()
