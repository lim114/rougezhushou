"""Exact shop-challenge references within the shared native reader."""
from .player_reference_window import ReferenceWindow, ToolPage
from .player_map_reader import REFERENCE_STYLE, make_reader
from . import current_cannot_reference as model


def open_reader(parent, target):
    host = parent.window()
    if not isinstance(host, ReferenceWindow):
        return None
    def context():
        if parent.result is None:
            return None
        current = model.target_for_enemy(parent.stage_id, parent.enemy_key)
        return (parent.result['source_identity'], current) if current else None
    def create(owner):
        from .current_cannot_view import CurrentCannotPanel
        reader = CurrentCannotPanel(target)
        if reader.result is None:
            reader.deleteLater()
            return None
        page = ToolPage('坎诺特与保险柜', reader, owner, object_name='mapReferenceWindow', extra_style=REFERENCE_STYLE)
        page.panel = reader
        page.finished.connect(reader._close_battle)
        page.resize(760, 600)
        return page
    return host.open_reference(parent, ('shop-vault-reference',), context, create)


def open_battle(panel, target):
    host = panel.window()
    if not isinstance(host, ReferenceWindow):
        return None
    from .current_battle_view import CurrentBattlePanel
    source = panel
    while not isinstance(source, ToolPage):
        source = source.parentWidget()
    def context():
        if panel.result is None or model.qualify_link(panel.result, target) is None:
            return None
        return panel.result['source_identity'], panel.target, panel.result['floor_declared'], target
    def select(reader):
        if target['enemy_key'] is not None:
            if not reader.enemy_choices.select_value(target['enemy_key'], emit=True):
                return False
            reader.tabs.setCurrentIndex(1)
        elif target['reward_id'] is not None:
            if not reader.rewards.choices.select_value(target['reward_id'], emit=True):
                return False
            reader.tabs.setCurrentWidget(reader.rewards)
        return True
    ancestor = source.source_parent
    while ancestor is not None:
        if isinstance(ancestor.panel, CurrentBattlePanel) and ancestor.panel.stage_id == target['stage_id']:
            original_enemy = ancestor.panel.enemy_key
            if not source.prepare() or not select(ancestor.panel):
                return False
            shown = host.parentWidget().present(ancestor)
            if original_enemy != ancestor.panel.enemy_key and source in host.linked_pages.values():
                # Changing the original enemy ends that enemy's reference chain.
                host.discard(source, fallback=ancestor)
            return shown
        ancestor = ancestor.source_parent
    def create(owner):
        page = make_reader('battle', {'id': target['stage_id'], 'title': '商店挑战'}, panel,
                           historical=True, page_owner=owner)
        if page is not None and not select(page.panel):
            page.deleteLater()
            return None
        return page
    role = ('shop-vault-battle', target['stage_id'], target['enemy_key'], target['reward_id'])
    return host.open_reference(panel, role, context, create)
