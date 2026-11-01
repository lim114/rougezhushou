"""Open verified current event panels in standalone or shared reference surfaces."""
from importlib import import_module
from PySide6.QtWidgets import QLabel
from . import current_node_readers as model

READERS = {
    'shadow346': ('current_shadow_view', 'CurrentShadowDialog'),
    'resting345': ('current_resting_view', 'CurrentRestingDialog'),
    'reconstruction344': ('current_reconstruction_view', 'CurrentReconstructionDialog'),
    'peace343': ('current_peace_view', 'CurrentPeaceDialog'),
    'scout342': ('current_scout_view', 'CurrentScoutDialog'),
    'portal341': ('current_portal_view', 'CurrentPortalDialog'),
    'agency340': ('current_agency_view', 'CurrentAgencyDialog'),
    'exit339': ('current_exit_view', 'CurrentExitDialog'),
    'memory336': ('current_memory_tree_view', 'CurrentMemoryTreeDialog'),
    'dog335': ('current_lone_dog_view', 'CurrentLoneDogDialog'),
    'cave334': ('current_cave_view', 'CurrentCaveDialog'),
    'vine333': ('current_vine_events_view', 'CurrentVineEventsDialog'),
    'rest': ('current_rest_travel_view', 'CurrentRestTravelDialog'),
    'shop': ('current_unattended_shop_view', 'CurrentUnattendedShopDialog'),
    'resources': ('current_resource_events_view', 'CurrentResourceEventsDialog'),
    'lake': ('current_lake_view', 'CurrentLakeDialog'),
    'encounters': ('current_encounters_view', 'CurrentEncountersDialog'),
    'sand': ('current_sand_view', 'CurrentSandDialog'),
    'ritual': ('current_ritual_view', 'CurrentRitualDialog'),
    'box': ('box_event_view', 'BoxEventDialog'),
}
EVENT_ARGUMENT_READERS = {'vine333', 'rest', 'resources', 'encounters', 'sand', 'ritual'}

def make_dialog(binding, parent=None, *, historical=False, page_owner=None):
    b = model.recheck(binding)
    if b is None:
        return None
    kind = b['reader']
    if kind not in READERS:
        return None
    module, name = READERS[kind]
    provider = import_module('.'+module, __package__)
    args = (b['current_event_id'],) if kind in EVENT_ARGUMENT_READERS else ()
    if page_owner is None:
        dialog = getattr(provider, name)(*args, parent=parent)
    else:
        from .player_reference_window import ToolPage
        from .player_map_reader import REFERENCE_STYLE
        panel = getattr(provider, name.replace('Dialog', 'Panel'))(*args)
        dialog = ToolPage(b['expected_summary']['title']+' · 事件资料', panel, page_owner,
                          object_name='mapReferenceWindow', extra_style=REFERENCE_STYLE)
        dialog.panel = panel
        if kind == 'sand':
            dialog.finished.connect(panel._close_related)
        elif kind == 'ritual':
            dialog.finished.connect(panel._close_material)
        dialog.finished.connect(panel._close_battle)
        dialog.resize(760, 600)
    if not model.matches_current(b, dialog.panel.result):
        dialog.close()
        dialog.deleteLater()
        return None
    banner = QLabel(('从历史节点打开的资料参考。' if historical else '从节点目录打开的资料参考。')+model.NOTICE)
    banner.setWordWrap(True)
    banner.setAccessibleName('当前事件资料的版本与范围')
    dialog.layout().insertWidget(0, banner)
    dialog.node_reference_banner = banner
    dialog.node_reference_binding = b
    if page_owner is None:
        from .player_map_reader import readable
        return readable(dialog)
    return dialog
