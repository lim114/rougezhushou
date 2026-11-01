"""Shared lifecycle for the seven existing exact-enemy mechanism readers."""
from dataclasses import dataclass
from importlib import import_module
from . import current_battle_reference as battle
from .player_window_frame import PlayerDialog


class EnemyMechanismDialog(PlayerDialog):
    def done(self,result):
        self.panel.clear_reference()
        super().done(result)


@dataclass(frozen=True)
class _Reader:
    provider: str
    dialog: str
    title: str
    availability: str = 'target_available'
    sync_result: str = 'result'
    check_battle_source: bool = True
    map_cleanup: str | None = None


_READERS = {
    'hanko': _Reader('current_hanko', 'CurrentHankoDialog', '汉科与烟雾 · 本关准确实体和机制', check_battle_source=False),
    'elbert': _Reader('current_elbert_reference', 'CurrentElbertDialog', '埃尔伯特与火种 · 本关机制', availability='locate', sync_result='base'),
    'sun_boss': _Reader('current_sun_boss', 'CurrentSunBossDialog', '沉沦之人 · 形态、信仰与地形条件', map_cleanup='_close_map'),
    'boss_documents': _Reader('current_boss_documents', 'CurrentBossDocumentsDialog', '本关完整机制 · 形态、循环与退场条件', map_cleanup='_close_map'),
    'guest_knights': _Reader('current_guest_knights', 'CurrentGuestKnightsDialog', '恶意讨薪 · 双骑士联动与完整招式', map_cleanup='close_owned_map'),
    'guest_crystals': _Reader('current_guest_crystals', 'CurrentGuestCrystalsDialog', '晶矿惊蝗 · 双晶兽的护盾与捕杀', map_cleanup='close_owned_map'),
    'guest_material': _Reader('current_guest_material', 'CurrentGuestMaterialDialog', '“物欲拮抗者” · 指令、屏障与斯第奇', map_cleanup='close_owned_map'),
}


def _available(parent, spec):
    provider = import_module('.' + spec.provider, __package__)
    if parent.result is None or parent.enemy_key is None:
        return False
    result = getattr(provider, spec.availability)(parent.stage_id, parent.enemy_key)
    return result is not None if spec.availability == 'locate' else bool(result)


def close_reader(parent, name):
    child = getattr(parent, name + '_dialog', None)
    if child is not None:
        child.reject()


def sync_reader(parent, name, keep):
    spec = _READERS[name]
    available = _available(parent, spec)
    button = getattr(parent, name + '_button')
    button.setVisible(available)
    button.setEnabled(available)
    child = getattr(parent, name + '_dialog', None)
    if child is None or not child.isVisible():
        return
    if not keep:
        close_reader(parent, name)
    elif not available:
        child.panel.clear_reference()
    else:
        child.panel.refresh_reference()
        if spec.check_battle_source:
            result = getattr(child.panel, spec.sync_result)
            if result is not None and result.get('battle_source_identity') != parent.result['source_identity']:
                close_reader(parent, name)


def open_reader(parent, name):
    if parent.result is None or parent.enemy_key is None:
        return False
    if battle.stage_reference(parent.stage_id) != parent.result:
        parent._clear()
        return False
    spec = _READERS[name]
    if not _available(parent, spec):
        close_reader(parent, name)
        getattr(parent, name + '_button').hide()
        return False
    view = import_module('.' + spec.provider.removesuffix('_reference') + '_view', __package__)
    from .player_reference_window import ReferenceWindow, ToolPage
    host = parent.window()
    if isinstance(host, ReferenceWindow):
        def context():
            if not _available(parent, spec):
                return None
            return parent.result['source_identity'], parent.stage_id, parent.enemy_key
        def qualified(panel):
            result = getattr(panel, spec.sync_result)
            return panel.result is not None and (not spec.check_battle_source or
                (result is not None and result.get('battle_source_identity') == parent.result['source_identity']))
        def create(owner):
            from .player_map_reader import REFERENCE_STYLE
            panel = getattr(view, spec.dialog.replace('Dialog', 'Panel'))(parent.stage_id, parent.enemy_key)
            if not qualified(panel):
                panel.deleteLater()
                return None
            page = ToolPage(spec.title, panel, owner, object_name='mapReferenceWindow', extra_style=REFERENCE_STYLE)
            page.panel = panel
            page.resize(760, 600)
            if spec.map_cleanup is not None:
                page.finished.connect(getattr(panel, spec.map_cleanup))
            if name == 'boss_documents':
                def select_enemy(key):
                    selected = parent._boss_documents_enemy_requested(key, reader=panel)
                    source = page.source_parent
                    shown = host.parentWidget().present(source)
                    if page in host.linked_pages.values():
                        host.discard(page, fallback=source)
                    return selected and shown
                panel.enemy_requested.connect(select_enemy)
            return page
        return host.open_reference(parent, ('enemy-mechanism', name), context, create, verify=qualified)
    close_reader(parent, name)
    child = getattr(view, spec.dialog)(parent.stage_id, parent.enemy_key, parent)
    setattr(parent, name + '_dialog', child)
    result = child.panel.result
    if result is None or (spec.check_battle_source and result.get('battle_source_identity') != parent.result['source_identity']):
        close_reader(parent, name)
        return False
    if name == 'boss_documents':
        child.panel.enemy_requested.connect(parent._boss_documents_enemy_requested)
    child.show()
    return True
