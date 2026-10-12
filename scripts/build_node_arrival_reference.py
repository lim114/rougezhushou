"""Freeze runtime reference data; source receipts are audit inputs, not UI state."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def build(root=ROOT):
    source=json.loads((root/'research/p3-node-arrival/source-receipt.json').read_text(encoding='utf8'))
    body=(root/source['community_file']).read_bytes()
    assert hashlib.sha256(body).hexdigest()==source['community_sha256']
    original=json.loads((root/'rouge/data/exploration-reference.json').read_text(encoding='utf8'))
    assert original['source']['commit']==source['game_commit']
    assert original['source']['sha256']==source['game_table_sha256']
    assert original['node_types']['LIGHT']==source['original_node_record']
    for phrase in ('获得1行动力','周围4格','周围12格','周围24格','保密等级·3+'):
        assert phrase in source['source_text']
    return {'schema_version':1,'source':source,
            'first_arrival_admission':{'original_type':'LIGHT','source_quantity':1,
                'first_entry_declaration_required':True,'reward_received_declaration_required':False,
                'repeated_behavior_verified':False},
            'visibility_count_parameters':{'base':{'spawn':4,'arrival':12},
                'upgraded':{'spawn':12,'arrival':24},'minimum_difficulty':3,
                'requires_split_unlocked':True,'range_geometry':None,'actual_revealed_nodes':None}}


if __name__=='__main__':
    (ROOT/'rouge/data/node-arrival-reference.json').write_text(
        json.dumps(build(),ensure_ascii=False,indent=2),encoding='utf8')
