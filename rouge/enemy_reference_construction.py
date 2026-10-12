"""Exact source path for fixed EnemyDataDbReference; never assumes missing modes."""
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path
@lru_cache(maxsize=1)
def construction_data():
    return json.loads((Path(__file__).with_name('data')/'enemy-reference-construction.json').read_text(encoding='utf-8'))
def source_path(binding,exact):
    mode=binding.get('use_db')
    result={'mode':None,'state':'unknown_reference_mode','compiled_result_available':False,
        'database_exact_level_available':bool(exact),'database_records_used':False,
        'overwritten_data_present':binding.get('overwritten_data_present') is True,
        'native_evidence':construction_data()['native_evidence'],
        'actual_runtime_binding_verified':False,'current_hotfix_equivalence_proven':False,
        'constructor_pointer_baseline_verified':False}
    if type(mode) is not bool:return result
    result['mode']='database' if mode else 'stage_constructor'
    if mode:
        result.update(state='exact_database_level_available' if exact else 'unavailable_exact_database_level',
            compiled_result_available=bool(exact),database_records_used=bool(exact))
    else:
        present=binding.get('overwritten_data_present') is True
        result.update(state='stage_constructor_overrides_available' if present else 'unavailable_constructor_overrides',
            compiled_result_available=present)
    return result

def configuration_path(reference):
    # Legacy internal scalar tests retain their explicit exact-level contract.
    # Real fixed queries always supply the source-bound construction record.
    path=reference.get('construction_reference')
    if path is not None:return deepcopy(path)
    exact=reference['exact_requested_level_present']
    return {'mode':'database','state':'exact_database_level_available' if exact else 'unavailable_exact_database_level',
        'compiled_result_available':exact,'database_records_used':exact,
        'constructor_pointer_baseline_verified':False}

def compiled_identity(binding,path):
    if path['mode']!='stage_constructor' or not path['compiled_result_available']:return None
    writes=binding.get('identity_overrides',{})
    key_known='prefabKey' in writes
    key=deepcopy(writes.get('prefabKey'))
    identity=binding.get('reference_id')
    alias_written=key_known and isinstance(identity,str) and bool(identity) and identity!=key
    return {'prefab_key':key,'prefab_key_written':key_known,'name':deepcopy(writes.get('name')),
        'description':deepcopy(writes.get('description')),
        'alias':identity if alias_written else None,'alias_written':alias_written,
        'key_in_level_reference':identity if alias_written else None,
        'alias_not_written_default_known':False,
        'rule':'nonempty reference id unequal to computed key writes alias; prefab key is preserved',
        'actual_spawn_or_resource_verified':False}
