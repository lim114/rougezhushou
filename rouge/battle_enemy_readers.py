"""Shared lifecycle for the seven existing exact-enemy mechanism readers."""
from dataclasses import dataclass
from importlib import import_module
from . import current_battle_reference as battle


@dataclass(frozen=True)
class _Reader:
    provider: str
    dialog: str
    availability: str = 'target_available'
    sync_result: str = 'result'
    check_battle_source: bool = True


_READERS = {
    'hanko': _Reader('current_hanko', 'CurrentHankoDialog', check_battle_source=False),
    'elbert': _Reader('current_elbert_reference', 'CurrentElbertDialog', availability='locate', sync_result='base'),
    'sun_boss': _Reader('current_sun_boss', 'CurrentSunBossDialog'),
    'boss_documents': _Reader('current_boss_documents', 'CurrentBossDocumentsDialog'),
    'guest_knights': _Reader('current_guest_knights', 'CurrentGuestKnightsDialog'),
    'guest_crystals': _Reader('current_guest_crystals', 'CurrentGuestCrystalsDialog'),
    'guest_material': _Reader('current_guest_material', 'CurrentGuestMaterialDialog'),
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
        child.panel.clear_reference()
        child.close()


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
