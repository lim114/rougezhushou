"""Shared reference navigation for existing event-to-stage readers."""
from .player_reference_window import ReferenceWindow, ToolPage


def event_context(panel):
    if panel.result is None:
        return None
    return (panel.result['source_identity'], panel.event_id, panel.scene_id, panel.choice_id,
            panel.reference_model.choice_reference(panel.result, panel.scene_id, panel.choice_id))


def _return_to_ancestor(panel, matches):
    page = panel
    while not isinstance(page, ToolPage):
        page = page.parentWidget()
    current = page
    page = page.source_parent
    while page is not None:
        if matches(page.panel):
            if not current.prepare():
                return False
            return panel.window().parentWidget().present(page)
        page = page.source_parent
    return None


def open_stage(panel, stage_id, *, context=None):
    host = panel.window()
    if not isinstance(host, ReferenceWindow):
        return None
    from .current_battle_view import CurrentBattlePanel
    returned = _return_to_ancestor(panel, lambda p: isinstance(p, CurrentBattlePanel) and p.stage_id == stage_id)
    if returned is not None:
        return returned
    from .player_map_reader import make_reader
    return host.open_reference(panel, ('fixed-stage', stage_id), context or (lambda: event_context(panel)),
        lambda owner: make_reader('battle', {'id': stage_id, 'title': '关联固定作战'},
                                  panel, historical=True, page_owner=owner))


def open_event_battles(panel, event_id, choice_id):
    host = panel.window()
    if not isinstance(host, ReferenceWindow):
        return None
    def create(owner):
        from .current_event_battles_view import CurrentEventBattlesPanel
        from .player_map_reader import REFERENCE_STYLE
        reader = CurrentEventBattlesPanel(event_id, choice_id)
        if reader.result is None:
            reader.deleteLater()
            return None
        page = ToolPage('关联作战 · 选项与配置', reader, owner,
                        object_name='mapReferenceWindow', extra_style=REFERENCE_STYLE)
        page.panel = reader
        page.finished.connect(reader._close_battle)
        page.finished.connect(reader._close_flow)
        page.resize(760, 600)
        return page
    return host.open_reference(panel, ('event-configurations', event_id, choice_id), lambda: event_context(panel), create)


def open_event_origins(panel):
    host = panel.window()
    if not isinstance(host, ReferenceWindow):
        return None
    def create(owner):
        from .current_event_battles_view import CurrentEventBattlesPanel
        from .player_map_reader import REFERENCE_STYLE
        reader = CurrentEventBattlesPanel(stage_id=panel.stage_id)
        if reader.result is None:
            reader.deleteLater()
            return None
        page = ToolPage('来源事件 · 选项与作战', reader, owner,
                        object_name='mapReferenceWindow', extra_style=REFERENCE_STYLE)
        page.panel = reader
        page.finished.connect(reader._close_battle)
        page.finished.connect(reader._close_flow)
        page.resize(760, 600)
        return page
    return host.open_reference(panel, ('stage-event-origins', panel.stage_id),
        lambda: None if panel.result is None else (panel.result['source_identity'], panel.stage_id), create)


def open_full_event(panel, kind, target):
    host = panel.window()
    if not isinstance(host, ReferenceWindow):
        return None
    from .current_encounters_view import CurrentEncountersPanel
    from .current_lake_view import CurrentLakePanel
    reader_class = CurrentLakePanel if kind == 'lake' else CurrentEncountersPanel
    if not target.get('phase_needed'):
        returned = _return_to_ancestor(panel, lambda p: isinstance(p, reader_class)
            and p.event_id == ('lake' if kind == 'lake' else target['event_id'])
            and p.scene_id == target['scene_id'] and p.choice_id == target['choice_id'])
        if returned is not None:
            return returned
    def create(owner):
        from .player_map_reader import REFERENCE_STYLE
        reader = reader_class(target) if kind == 'lake' else reader_class(
            target['event_id'], target['scene_id'], target['choice_id'])
        if reader.result is None:
            reader.deleteLater()
            return None
        page = ToolPage('完整事件 · 选项与后续', reader, owner,
                        object_name='mapReferenceWindow', extra_style=REFERENCE_STYLE)
        page.panel = reader
        page.finished.connect(reader._close_battle)
        page.resize(760, 600)
        return page
    return host.open_reference(panel, ('full-event', kind), lambda: None if panel.result is None else (
        panel.result['source_identity'], panel.choice_id, panel._flow_target(panel.choice_id)), create)


def open_fixed_map(panel, stage_id, *, context, verify):
    host = panel.window()
    if not isinstance(host, ReferenceWindow):
        return None
    def create(owner):
        from .current_map_position_view import CurrentMapPositionPanel
        from .player_map_reader import REFERENCE_STYLE
        reader = CurrentMapPositionPanel(stage_id)
        if reader.result is None:
            reader.deleteLater()
            return None
        page = ToolPage('固定地图 · 地形与格子', reader, owner,
                        object_name='mapReferenceWindow', extra_style=REFERENCE_STYLE)
        page.panel = reader
        page.resize(900, 650)
        return page
    return host.open_reference(panel, ('mechanism-map', stage_id), context, create, verify=verify)
