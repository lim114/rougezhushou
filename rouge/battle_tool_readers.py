"""Source-bound tool and position readers within the shared reference window."""
from importlib import import_module
from .player_reference_window import ReferenceWindow, ToolPage
from .player_map_reader import REFERENCE_STYLE


TOOLS = {
    'spawn_candidates': ('current_spawn_candidates_view', 'CurrentSpawnCandidatesPanel', '出怪候选与关联记录', '_spawn_action_selected'),
    'enemy_spawns': ('current_enemy_spawns_view', 'CurrentEnemySpawnsPanel', '所选敌人的出怪记录', '_enemy_spawns_action_selected'),
    'stage_objects': ('current_stage_objects_view', 'CurrentStageObjectsPanel', '本关物件与机关', '_stage_objects_action_selected'),
    'route_itinerary': ('current_route_itinerary_view', 'CurrentRouteItineraryPanel', '敌人行程与停留条件', '_route_itinerary_action_selected'),
}
POSITIONS = {
    'map': ('current_map_position_view', 'CurrentMapPositionPanel', '固定地图 · 地形与格子'),
    'action': ('current_action_positions_view', 'CurrentActionPositionsPanel', '出怪与装置 · 地图位置'),
    'object': ('current_stage_objects_view', 'CurrentObjectPositionPanel', '物件 · 地图位置'),
    'route': ('current_route_itinerary_view', 'CurrentRouteStepPositionPanel', '行程环节 · 地图位置'),
}


def open_tool(parent, name):
    host = parent.window()
    if not isinstance(host, ReferenceWindow):
        return None
    module, panel_name, title, action_handler = TOOLS[name]
    args = (parent.stage_id, parent.enemy_key) if name == 'enemy_spawns' else (parent.stage_id,)
    def context():
        if parent.result is None:
            return None
        return (parent.result['source_identity'], parent.stage_id,
                parent.enemy_key if name == 'enemy_spawns' else None)
    def qualified(reader):
        return reader.result is not None and reader.result['battle_source_identity'] == parent.result['source_identity']
    def create(owner):
        reader = getattr(import_module('.'+module, __package__), panel_name)(*args)
        if not qualified(reader):
            reader.deleteLater()
            return None
        page = ToolPage(title, reader, owner, object_name='mapReferenceWindow', extra_style=REFERENCE_STYLE)
        page.panel = reader
        page.resize(760, 600)
        def follow(key, *, position=False):
            if not getattr(parent, action_handler)(key, reader=reader):
                return False
            if position:
                return open_position(reader, 'action', (parent.stage_id, key))
            return owner.present(page.source_parent)
        reader.actionSelected.connect(follow)
        if name in ('spawn_candidates', 'enemy_spawns'):
            reader.actionPositionRequested.connect(lambda key: follow(key, position=True))
        return page
    return host.open_reference(parent, ('battle-tool', name), context, create, verify=qualified)


def open_position(parent, kind, args, *, context=None):
    host = parent.window()
    if not isinstance(host, ReferenceWindow):
        return None
    module, panel_name, title = POSITIONS[kind]
    def selected_context():
        return (parent.result['source_identity'], parent._view_key) if parent.result else None
    def create(owner):
        reader = getattr(import_module('.'+module, __package__), panel_name)(*args)
        if reader.result is None:
            reader.deleteLater()
            return None
        label=title
        if kind in('map','action'):
            grid=reader.result if kind=='map'else reader.result['grid']
            label=grid['stage_name']+(' · 紧急'if grid['is_elite']else'')+' · '+title
        page = ToolPage(label, reader, owner, object_name='mapReferenceWindow', extra_style=REFERENCE_STYLE)
        page.panel = reader
        page.resize(960, 640)
        return page
    return host.open_reference(parent, ('battle-position', kind), context or selected_context, create)
