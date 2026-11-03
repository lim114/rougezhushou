"""Separate historical program provenance from unchanged public runtime data."""
from hashlib import sha256
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
PACK='research/runtime-reference-loaders-20261031'
RECIPES={
    'battle-events':'research/p3-battle-entry-compatibility-299/source-manifest.json',
    'named-items':'research/p3-named-reward-items-301/source-manifest.json',
    'ritual':'research/p3-ritual-weakening-302/source-manifest.json',
    'recruitment':'research/p3-choice-recruitment-290/source-manifest.json',
    'current-rewards':'research/p3-current-rewards-315/runtime-manifest.json',
    'event-named-links':'research/p3-event-named-rewards-289/source-manifest.json',
    'moving-rewards':'research/p3-moving-reward-current/source-manifest.json',
    'peace-guardian':'research/p3-peace-guardian-results-291/source-manifest.json',
    'resting-corner':'research/p3-resting-results-293/source-manifest.json',
    'stage-entry':'research/p3-stage-entry-configuration-296/manifest.json',
}


def pin(path):
    raw=(ROOT/path).read_bytes()
    return {'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}


def build():
    result={}
    for name,recipe in RECIPES.items():
        original=json.loads((ROOT/recipe).read_bytes())
        code={p:v for p,v in original['files'].items() if p.endswith(('.py','.js','.cjs'))}
        runtime=original.get('runtime_files',original['files'])
        for path,expected in runtime.items():
            if path not in code:assert pin(path)==expected,path
        manifest=dict(original)
        if 'runtime_files' in manifest:
            manifest['runtime_files']={p:v for p,v in runtime.items() if p not in code}
        else:
            manifest['files']={p:v for p,v in original['files'].items() if p not in code}
        if 'compatibility_rebinding' in manifest:
            manifest['historical_compatibility_rebinding']=manifest.pop('compatibility_rebinding')
        manifest['historical_recipe_manifest']={'path':recipe,**pin(recipe)}
        manifest['historical_recipe_code_sources']=code
        manifest['runtime_policy']='Verify all selected public data, authority and document bytes; program source is historical build provenance. Exact typed API comparisons, cache checks and token identity remain in the reviewed program.'
        path=ROOT/PACK/name/'source-manifest.json'
        raw=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf8')
        if path.exists():assert path.read_bytes()==raw,'Existing snapshot differs: '+str(path)
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        result[name]={'path':path.relative_to(ROOT).as_posix(),**pin(path),'historical_code_sources':len(code),
                      'runtime_files':len(manifest.get('runtime_files',manifest['files']))}
    return result


if __name__=='__main__':print(json.dumps(build(),ensure_ascii=False))
