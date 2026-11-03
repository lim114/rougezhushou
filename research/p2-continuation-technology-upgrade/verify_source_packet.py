"""Re-read the complete original commonDevelopment and the pinned public rule."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser()
    parser.add_argument('--topic-table', type=Path, required=True)
    parser.add_argument('--public-page', type=Path, required=True)
    args = parser.parse_args()
    packet = json.loads((root / 'rouge/data/p2-technology-upgrade-source.json').read_text(encoding='utf-8'))
    raw = args.topic_table.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == packet['source']['sha256']
    original = json.loads(raw)['customizeData']['rogue_6']['commonDevelopment']
    assert packet['common_development_raw'] == original
    assert hashlib.sha256(args.public_page.read_bytes()).hexdigest() == packet['public_rule']['sha256']
    nodes = original['developments']; gates = original['developmentsDifficultyNodeInfos']
    assert len(nodes) == 57 and len(gates) == 3
    assert [gate['enableGrade'] for gate in gates.values()] == [3, 6, 9]
    assert all(nodes[identity]['nodeType'] == 'DIFFICULTY' and nodes[identity]['tokenCost'] == 0 for identity in gates)
    assert all(type(node['tokenCost']) is int and node['tokenCost'] >= 0 for node in nodes.values())
    assert all(target in nodes for node in nodes.values() for target in node['frontNodeId'])
    print(json.dumps({'passed': True, 'full_original_common_development_matches': True,
                      'node_costs_rechecked': 57, 'automatic_gates_rechecked': 3,
                      'public_page_revision': packet['public_rule']['revision_id'],
                      'ordinary_prerequisite_logic_verified': False,
                      'actual_account_or_activation_verified': False}, ensure_ascii=False))


if __name__ == '__main__': main()
