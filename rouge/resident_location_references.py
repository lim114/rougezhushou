"""CACHE CANDIDATE: pure position references from a supplied map record only.

No game/run/file access, nearest search, route, completed-battle inference or
actual movement. ``epoch`` and ``historical`` come from the caller's map context.
The graph schema is the existing map_recognition/MapView grid + nodes schema.
"""
from copy import deepcopy


RESIDENT_TYPE = '“居民”据点'
REFERENCE_KIND = 'resident_location_reference'


def _identity(value):
    return type(value) is str and bool(value.strip())


def _position(node, rows):
    # Same labels/order as rouge.map_reporting.location; no combat-row reversal.
    row = ('上排', '中排', '下排')[node['row']] if rows == 3 else f"第{node['row']+1}排"
    return f"{row} · 第{node['col']+1}列"


def _checked_graph(graph):
    if type(graph) is not dict:
        return None, 'invalid_graph'
    if not _identity(graph.get('zone_id')) or not _identity(graph.get('template_id')):
        return None, 'invalid_map_identity'
    grid = graph.get('grid')
    if type(grid) is not dict:
        return None, 'invalid_grid'
    rows, cols = grid.get('rows'), grid.get('cols')
    if type(rows) is not int or type(cols) is not int or rows <= 0 or cols <= 0:
        return None, 'invalid_grid'
    nodes = graph.get('nodes')
    if type(nodes) is not list:
        return None, 'invalid_nodes'
    ids, positions = set(), set()
    for node in nodes:
        if type(node) is not dict or not _identity(node.get('id')):
            return None, 'invalid_node_identity'
        if node['id'] in ids:
            return None, 'duplicate_node_id'
        row, col = node.get('row'), node.get('col')
        if type(row) is not int or type(col) is not int or not (0 <= row < rows and 0 <= col < cols):
            return None, 'invalid_node_position'
        if (row, col) in positions:
            return None, 'duplicate_node_position'
        for key in ('observed_type', 'remembered_type'):
            if node.get(key) is not None and type(node[key]) is not str:
                return None, 'invalid_type_evidence'
        ids.add(node['id'])
        positions.add((row, col))
    return (rows, cols, nodes), None


def resident_location_references(graph, *, epoch, historical):
    """Return read/history locations, never a destination or completion decision.

    All nodes are structurally checked before any location is exposed. Unknown
    or empty references do not prove that the map contains no resident post.
    No directory floor, template candidate, title, distance or visit flag is used.
    """
    result = {
        'status': 'unknown', 'scope': 'provided_map_position_only', 'rows': [],
        'reason_codes': [], 'default_binding': None,
        'actual_target_node_id': None, 'actual_moved': None,
        'actual_current_floor_completion': None, 'actual_battle_triggered': None,
        'actual_position_after': None, 'actual_route': None,
        'notice': '地图位置资料尚未核对，暂不列出据点；不表示本图没有据点。',
    }
    if not _identity(epoch) or type(historical) is not bool:
        result['reason_codes'] = ['invalid_map_context']
        return result
    if graph is None:
        result.update(status='no_graph', reason_codes=['no_map_record'],
                      notice='尚无可用地图记录；本次目的地、移动和据点完成情况仍未知。')
        return result
    checked, error = _checked_graph(graph)
    if error:
        result['reason_codes'] = [error]
        return result
    rows, cols, nodes = checked
    references = []
    # Spatial order helps find a location; it is not a route or target ranking.
    for node in sorted(nodes, key=lambda item: (item['row'], item['col'], item['id'])):
        observed, remembered = node.get('observed_type'), node.get('remembered_type')
        if observed == RESIDENT_TYPE:
            role = 'current_observed'
            evidence_label = '记录时读到的据点' if historical else '已读据点'
        elif remembered == RESIDENT_TYPE:
            role = 'historical_remembered'
            evidence_label = '以前读到的据点'
        else:
            continue
        binding = {
            'reference_kind': REFERENCE_KIND,
            'epoch': epoch, 'zone_id': graph['zone_id'], 'template_id': graph['template_id'],
            'node_id': node['id'], 'row': node['row'], 'col': node['col'],
            'grid': {'rows': rows, 'cols': cols},
            'type_evidence_role': role, 'map_historical': historical,
            'observed_type': observed, 'remembered_type': remembered,
        }
        location = _position(node, rows)
        references.append({
            'node_id': node['id'], 'location': location,
            'label': location + ' · ' + evidence_label + (' · 历史地图记录' if historical else ''),
            'type_evidence_role': role, 'map_historical': historical,
            'binding': deepcopy(binding),
        })
    result.update(status='available', rows=references,
        notice=('这些是所提供地图记录中已读或记住的据点位置，不代表本次移动目的地；历史位置不证明作战已完成。'
                if references else
                '当前地图记录没有可列出的已读或历史据点位置；这不证明地图中没有据点。'))
    return result


def _same_json(value, expected):
    if type(value) is not type(expected):
        return False
    if type(expected) is dict:
        return (value.keys() == expected.keys() and all(type(key) is str for key in value)
                and all(_same_json(value[key], expected[key]) for key in expected))
    if type(expected) is list:
        return len(value) == len(expected) and all(_same_json(a, b) for a, b in zip(value, expected))
    return value == expected


def resident_binding_matches(graph, binding, *, epoch, historical):
    """Rebuild current evidence; reject stale, partial or type-coerced bindings."""
    if type(binding) is not dict:
        return False
    reference = resident_location_references(graph, epoch=epoch, historical=historical)
    if reference['status'] != 'available':
        return False
    return any(_same_json(binding, row['binding']) for row in reference['rows'])
