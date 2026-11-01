"""The existing documented-event routes, shared by workspace and note readers."""
from importlib import import_module

# Keep the established locator order and each reader's constructor arguments.
READERS = (
    ('current_startup', 'CurrentStartupDialog', (None,)),
    ('current_shadow', 'CurrentShadowDialog', (None,)),
    ('current_resting', 'CurrentRestingDialog', (None,)),
    ('current_reconstruction', 'CurrentReconstructionDialog', (None,)),
    ('current_peace', 'CurrentPeaceDialog', ('scene_id', 'choice_id')),
    ('current_scout', 'CurrentScoutDialog', ('scene_id', 'choice_id')),
    ('current_portal', 'CurrentPortalDialog', (None,)),
    ('current_agency', 'CurrentAgencyDialog', ('scene_id', 'choice_id')),
    ('current_exit', 'CurrentExitDialog', (None,)),
    ('current_memory_tree', 'CurrentMemoryTreeDialog', ('scene_id', 'choice_id')),
    ('current_lone_dog', 'CurrentLoneDogDialog', ('scene_id', 'choice_id')),
    ('current_cave', 'CurrentCaveDialog', (None,)),
    ('current_vine_events', 'CurrentVineEventsDialog', ('event_id', 'scene_id', 'choice_id')),
    ('current_rest_travel', 'CurrentRestTravelDialog', ('event_id', None)),
    ('current_unattended_shop', 'CurrentUnattendedShopDialog', (None,)),
    ('current_resource_events', 'CurrentResourceEventsDialog', ('event_id', 'scene_id', 'choice_id')),
    ('current_lake', 'CurrentLakeDialog', (None,)),
    ('current_encounters', 'CurrentEncountersDialog', ('event_id', 'scene_id', 'choice_id')),
    ('current_sand_reference', 'CurrentSandDialog', ('event_id', 'scene_id', 'choice_id')),
    ('current_ritual_reference', 'CurrentRitualDialog', ('event_id', 'scene_id', 'choice_id')),
)


def reader_plan(category, identity):
    for module, name, fields in READERS:
        target = import_module('.'+module, __package__).locate(category, identity)
        if target is not None:
            return module.removesuffix('_reference')+'_view', name, tuple(target if field is None else target[field] for field in fields)
    from .documented_event_flows import event_for_scene
    event_id = event_for_scene(identity) if category == 'scenes' else None
    if event_id is not None:
        return 'documented_event_flow_view', 'DocumentedEventFlowDialog', (event_id, identity)
    from .box_event_reference import locate
    target = locate(category, identity)
    if target is not None:
        return 'box_event_view', 'BoxEventDialog', (target['scene_id'], target['choice_id'])
    return None


def make_flow_reader(plan, parent=None, *, page_owner=None):
    module, name, args = plan
    provider = import_module('.'+module, __package__)
    if page_owner is None:
        dialog = getattr(provider, name)(*args, parent=parent)
        if dialog.panel.result is None:
            dialog.close(); dialog.deleteLater(); return None
        return dialog
    from .player_reference_window import ToolPage
    from .player_map_reader import REFERENCE_STYLE
    from PySide6.QtWidgets import QPushButton
    panel = getattr(provider, name.replace('Dialog', 'Panel'))(*args)
    if panel.result is None:
        panel.deleteLater(); return None
    page = ToolPage('完整事件 · '+panel.result['event']['title'], panel, page_owner,
                    object_name='mapReferenceWindow', extra_style=REFERENCE_STYLE)
    page.panel = panel
    page.finished.connect(panel._close_battle)
    if module == 'current_sand_view':page.finished.connect(panel._close_related)
    if module == 'current_ritual_view':page.finished.connect(panel._close_material)
    for button in panel.findChildren(QPushButton):button.setAutoDefault(False)
    page.resize(760, 600)
    return page
