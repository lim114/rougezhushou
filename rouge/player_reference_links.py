"""Shared reference navigation for existing event-to-stage readers."""
from .player_reference_window import ReferenceWindow, ToolPage


def open_overlay_web(companion,target,area):
    """Reuse the shared reference window; this page outlives map eligibility."""
    from .tomimi_view import TomimiPanel
    page=companion.overlay_web_pages.get(target['url'])
    if page is None:
        reader=TomimiPanel(target)
        page=ToolPage(target.get('provider','Tomimi')+' · '+target['name'],reader,companion,object_name='mapReferenceWindow')
        page.panel=reader;page.resize(min(1100,round(area.width()*.65)),min(680,round(area.height()*.65)))
        reader.layout().removeWidget(reader.navigation);reader.layout().removeWidget(reader.address)
        reader.navigation_bar.insertWidget(3,reader.address,1);reader.title.hide();reader.environment.hide()
        reader.navigation.setObjectName('overlayWebNav');reader.navigation.setStyleSheet('#overlayWebNav{background:#f2f3f5;border-radius:6px;} #overlayWebNav QLineEdit{color:#252a30;background:#ffffff;border:0;border-radius:6px;padding:4px;} #overlayWebNav QToolButton{background:transparent;border:0;padding:3px;} #overlayWebNav QLabel{color:#44505b;background:transparent;}')
        page.title_label.hide();page.header_bar.addWidget(reader.navigation,1)
        page.setProperty('mapOverlayWebPage',True);page.setProperty('playerOpened',True);companion.overlay_web_pages[target['url']]=page
    companion.present(page)
    host=companion.reference_window;host.resize(page.preferred_size);host.move(area.center()-host.rect().center())
    return page


def event_context(panel):
    if panel.result is None:
        return None
    return (panel.result['source_identity'], panel.event_id, panel.scene_id, panel.choice_id,
            panel.reference_model.choice_reference(panel.result, panel.scene_id, panel.choice_id))


def _return_to_ancestor(panel, host, matches):
    page = panel
    while not isinstance(page, ToolPage):
        page = page.parentWidget()
    current = page
    page = page.source_parent
    while page is not None:
        if matches(page.panel):
            if not current.prepare():
                return False
            return host.parentWidget().present(page)
        page = page.source_parent
    return None


def open_stage(panel, stage_id, *, context=None):
    host = panel.window()
    if not isinstance(host, ReferenceWindow):
        return None
    from .current_battle_view import CurrentBattlePanel
    returned = _return_to_ancestor(panel, host, lambda p: isinstance(p, CurrentBattlePanel) and p.stage_id == stage_id)
    if returned is not None:
        return returned
    from .player_map_reader import make_reader
    return host.open_reference(panel, ('fixed-stage', stage_id), context or (lambda: event_context(panel)),
        lambda owner: make_reader('battle', {'id': stage_id, 'title': '关联固定作战'},
                                  panel, historical=True, page_owner=owner))


def _event_battles_page(owner, title, *, event_id=None, choice_id=None, stage_id=None):
    from .current_event_battles_view import CurrentEventBattlesPanel
    from .player_map_reader import REFERENCE_STYLE
    reader = CurrentEventBattlesPanel(event_id=event_id, choice_id=choice_id, stage_id=stage_id)
    if reader.result is None:
        reader.deleteLater()
        return None
    page = ToolPage(title, reader, owner, object_name='mapReferenceWindow', extra_style=REFERENCE_STYLE)
    page.panel = reader
    page.finished.connect(reader._close_battle)
    page.finished.connect(reader._close_flow)
    page.resize(760, 600)
    return page


def open_event_battles(panel, event_id, choice_id):
    host = panel.window()
    if not isinstance(host, ReferenceWindow):
        return None
    return host.open_reference(panel, ('event-configurations', event_id, choice_id), lambda: event_context(panel),
        lambda owner: _event_battles_page(owner, '关联作战 · 选项与配置', event_id=event_id, choice_id=choice_id))


def open_event_origins(panel):
    host = panel.window()
    if not isinstance(host, ReferenceWindow):
        return None
    return host.open_reference(panel, ('stage-event-origins', panel.stage_id),
        lambda: None if panel.result is None else (panel.result['source_identity'], panel.stage_id),
        lambda owner: _event_battles_page(owner, '来源事件 · 选项与作战', stage_id=panel.stage_id))


def open_full_event(panel, kind, target):
    host = panel.window()
    if not isinstance(host, ReferenceWindow):
        return None
    from .current_encounters_view import CurrentEncountersPanel
    from .current_lake_view import CurrentLakePanel
    reader_class = CurrentLakePanel if kind == 'lake' else CurrentEncountersPanel
    if not target.get('phase_needed'):
        returned = _return_to_ancestor(panel, host, lambda p: isinstance(p, reader_class)
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


def open_material_source(panel, source):
    from . import current_ritual_reference as model
    def context():
        current = model.acquisition_reference(panel.result, panel.scene_id, panel.choice_id) if panel.result else None
        return (event_context(panel), current) if current else None
    if source['kind'] == 'battle':
        return open_stage(panel, source['stage_id'], context=context)
    host = panel.window()
    if not isinstance(host, ReferenceWindow):
        return None
    if source['kind'] == 'event':
        target = model.locate('choices', source['source_choice_id'])
        if target is None:
            panel.clear_reference()
            return False
        from .current_ritual_view import CurrentRitualPanel
        returned = _return_to_ancestor(panel, host, lambda p: isinstance(p, CurrentRitualPanel)
            and (p.event_id, p.scene_id, p.choice_id) == (target['event_id'], target['scene_id'], target['choice_id']))
        if returned is not None:
            return returned
    elif source['kind'] == 'exchange':
        from .current_exchange_reference import target_entry
        target = target_entry('choices', source['source_choice_id'])
        if target is None:
            panel._sync_extra()
            return False
    else:
        return False
    def create(owner):
        from .player_map_reader import REFERENCE_STYLE
        if source['kind'] == 'event':
            reader = CurrentRitualPanel(target['event_id'], target['scene_id'], target['choice_id'])
        else:
            from .current_exchange_view import CurrentExchangePanel
            reader = CurrentExchangePanel(target)
        if reader.result is None:
            reader.deleteLater()
            return None
        title = '材料来源 · '+reader.result['event']['title'] if source['kind'] == 'event' else '材料来源 · 回滚文明'
        page = ToolPage(title, reader, owner, object_name='mapReferenceWindow', extra_style=REFERENCE_STYLE)
        page.panel = reader
        page.resize(760, 600)
        if source['kind'] == 'event':
            page.finished.connect(reader._close_battle)
            page.finished.connect(reader._close_material)
        else:
            from PySide6.QtWidgets import QPushButton
            recipe = QPushButton('查看复原条件')
            recipe.setAutoDefault(False)
            recipe.setAccessibleName('查看这件材料的复原条件')
            def read_recipe():
                if not page.prepare():
                    return False
                group = next((g for g in reader.result['data']['document_groups']
                    if source['recipe_choice_id'] in g['primary_candidate_ids']), None)
                if group is None:
                    return False
                reader.tabs.setCurrentIndex(1)
                reader._select(reader.groups, group['id'])
                return True
            recipe.clicked.connect(read_recipe)
            page.header_bar.addWidget(recipe)
        return page
    return host.open_reference(panel, ('material-source', source['kind']), context, create)
