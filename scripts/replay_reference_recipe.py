"""Replay an unchanged historical public-data builder in a temporary source tree."""
from contextlib import redirect_stdout
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse,io,json,runpy,sys

ROOT=Path(__file__).resolve().parents[1]
RECIPES={
    'named-items':('scripts/build_named_reward_items_301.py','research/p3-named-reward-items-301/source-manifest.json'),
    'ritual':('scripts/build_ritual_weakening_302.py','research/p3-ritual-weakening-302/source-manifest.json'),
}


def replay(recipe):
    script,manifest_name=RECIPES[recipe]
    manifest=json.loads((ROOT/manifest_name).read_bytes())
    namespace=runpy.run_path(str(ROOT/script))
    context=namespace['main'].__globals__
    names={manifest_name,context['CONFIG'],*manifest['files']}
    with TemporaryDirectory(prefix='rouge-public-recipe-')as folder:
        target_root=Path(folder);historical=[]
        for name in sorted(names):
            relative=Path(name)
            if relative.is_absolute()or '..'in relative.parts or relative.parts[0]not in ('rouge','research','scripts','verification'):raise ValueError('Public recipe path required.')
            raw=(ROOT/name).read_bytes();expected=manifest['files'].get(name)
            if expected and sha256(raw).hexdigest()!=expected['sha256']:
                archived=ROOT/'research/runtime-reference-loaders-20261031/baseline/historical-299'/name
                if not name.endswith('.py')or not archived.is_file():raise ValueError('Historical input unavailable: '+name)
                raw=archived.read_bytes();historical.append(name)
            if expected:assert len(raw)==expected['bytes']and sha256(raw).hexdigest()==expected['sha256'],name
            target=target_root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        context['ROOT']=target_root
        before_argv=sys.argv;stream=io.StringIO()
        try:
            sys.argv=[script]
            with redirect_stdout(stream):namespace['main']()
        finally:sys.argv=before_argv
        report=json.loads(stream.getvalue())
        assert report['write']is False
        report.update(historical_code_inputs_used_only_as_guard_bytes=historical,
                      isolated_public_source_tree=True,original_builder_sha256=sha256((ROOT/script).read_bytes()).hexdigest())
        return report


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--recipe',choices=RECIPES,required=True);args=parser.parse_args()
    print(json.dumps(replay(args.recipe),ensure_ascii=False,indent=2))
