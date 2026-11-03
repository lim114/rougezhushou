"""Read-only route references; a revealed node is not proof of completion.

Walking rules are documented in .cache/research/routes-049/evidence.json.
Template edges remain community topology, not independently observed edges.
"""
from collections import deque


def _pass_through(node):
    # Past visits, predicted types and old names do not prove the present tile.
    return bool(node.get('visible') and
                node.get('observed_type') in ('林间空地', '曲折密道'))


def _revealed(node):
    label = node.get('observed_type')
    return bool(node.get('visible') and label and not label.startswith('未知'))


def _shortest(nodes, adjacency, start, target, *, corridor=False):
    """Return one stable shortest path plus the count of equally short paths."""
    distances = {start: 0}; parents = {}; counts = {start: 1}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        if current == target:
            continue
        for other in sorted(adjacency[current], key=lambda key:
                            (nodes[key]['row'], nodes[key]['col'], key)):
            if corridor and other != target and not _pass_through(nodes[other]):
                continue
            distance = distances[current]+1
            if other not in distances:
                distances[other] = distance; parents[other] = current
                counts[other] = counts[current]; queue.append(other)
            elif distances[other] == distance:
                counts[other] += counts[current]
    if target not in distances:
        return None
    path = [target]
    while path[-1] != start:
        path.append(parents[path[-1]])
    path.reverse()
    return {'path': path, 'steps': distances[target], 'equal_shortest_paths': counts[target]}


def route_reference(graph, target, *, historical=False):
    """Separate pure topology from paths whose intermediate types permit walking.

    No route is a command or a guarantee of safe entry. Occupancy, fog, actual
    AP, cost modifiers and some completion markers are not currently read.
    """
    result = {'status': 'unavailable', 'display_path': [], 'corridor': None,
              'topology': None, 'entry_confirmed': False}
    if not graph or graph.get('status') != 'matched':
        result['reason'] = 'layout_unconfirmed'; return result
    if historical:
        result['reason'] = 'historical_frame'; return result
    entries = graph.get('nodes', [])
    nodes = {n['id']: n for n in entries}
    if len(nodes) != len(entries):
        result['reason'] = 'invalid_graph'; return result
    if target not in nodes:
        result['reason'] = 'target_unconfirmed'; return result
    start = graph.get('current_node')
    if not start or start not in nodes:
        result['reason'] = 'current_unconfirmed'; return result
    result.update(start=start, target=target)
    if start == target:
        result.update(status='same_position', display_path=[start])
        return result
    adjacency = {key: set() for key in nodes}
    for edge in graph.get('edges', []):
        if len(edge) != 2 or edge[0] not in nodes or edge[1] not in nodes or edge[0] == edge[1]:
            result['reason'] = 'invalid_graph'; return result
        a, b = edge; adjacency[a].add(b); adjacency[b].add(a)
    topology = _shortest(nodes, adjacency, start, target)
    if not topology:
        result['reason'] = 'disconnected'; return result
    topology['unconfirmed_intermediate_nodes'] = [key for key in topology['path'][1:-1]
                                                 if not _pass_through(nodes[key])]
    corridor = _shortest(nodes, adjacency, start, target, corridor=True) if _revealed(nodes[target]) else None
    if corridor:
        # This is base walking consumption, not net AP or an affordability test.
        corridor['base_walking_ap'] = corridor['steps']
    result.update(status='reference', topology=topology, corridor=corridor,
                  target_revealed=_revealed(nodes[target]),
                  display_path=(corridor or topology)['path'])
    return result
