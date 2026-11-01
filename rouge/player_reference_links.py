"""Shared reference navigation for existing event-to-stage readers."""
from .player_reference_window import ReferenceWindow, ToolPage


def event_context(panel):
    if panel.result is None:
        return None
    return (panel.result['source_identity'], panel.event_id, panel.scene_id, panel.choice_id,
            panel.reference_model.choice_reference(panel.result, panel.scene_id, panel.choice_id))


def open_stage(panel, stage_id, *, context=None):
    host = panel.window()
    if not isinstance(host, ReferenceWindow):
        return None
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
