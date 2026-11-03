"""Check exact public terrain provenance and whole fixed-grid coverage, read-only."""
from pathlib import Path
from hashlib import sha256
import json,sys,argparse
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true',required=True);p.parse_args()
    from rouge import current_terrain_directory as model,current_battle_reference as battle
    notes=json.loads((R/'research/p3-current-terrain-directory-378/source-notes.json').read_bytes())
    for name,pin in notes['sources'].items():
        path=R/name;assert path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(R.resolve());raw=path.read_bytes()
        assert len(raw)==pin['bytes'] and sha256(raw).hexdigest()==pin['sha256'],name
    ref=model.packet();current=battle.packet();assert ref is not None and current is not None
    expected={}
    for sid,s in current['version']['current']['details']['stages'].items():
        level=current['inputs']['levels']['levels/'+s['levelId'].lower()+'.json']
        for r,line in enumerate(level['mapData']['map']):
            for c,index in enumerate(line):expected[(sid,r,c)]=(index,level['mapData']['tiles'][index])
    actual={}
    for row in ref['rows']:
        for r,c in row['cells']:
            key=(row['stage_id'],r,c);assert key not in actual;actual[key]=(row['tile_index'],row['tile'])
    assert expected==actual;assert len({tuple(r['key']) for r in ref['rows']})==len(ref['rows'])
    assert ref['actual_occurrence']is None and not ref['run_updated']
    print(json.dumps({'passed':True,'source_pins':len(notes['sources']),'stage_configurations':ref['stage_count'],'exact_grid_cells':len(actual),'terrain_declarations_in_use':len(ref['rows']),'actual_effect_or_deployment_claimed':False,'source_files_modified':False},ensure_ascii=False))
if __name__=='__main__':main()
