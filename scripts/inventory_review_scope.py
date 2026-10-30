"""Inventory tracked application sources without executing modules or reading private data.

An import inventory is a review map, not proof of runtime reachability/correctness.
"""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import ast, argparse, json, subprocess

ROOT=Path(__file__).resolve().parents[1]


def inventory():
    names=subprocess.check_output(['git','ls-files','-z','rouge'],cwd=ROOT).decode('utf-8').split('\0')
    rows=[]
    for name in sorted(n for n in names if n.endswith(('.py','.cjs'))):
        raw=(ROOT/name).read_bytes()
        row={'path':name,'sha256':sha256(raw).hexdigest(),'bytes':len(raw),'lines':len(raw.splitlines()),
             'role':'verification_support' if 'acceptance' in Path(name).stem else 'application_source',
             'correctness_review_complete':False}
        if name.endswith('.py'):
            tree=ast.parse(raw.decode('utf-8-sig'),filename=name)
            row['syntax_parsed']=True
            row['function_count']=sum(isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) for n in ast.walk(tree))
            row['declared_imports']=sorted({('from '+'.'*n.level+(n.module or '')+' import '+','.join(a.name for a in n.names))
                if isinstance(n,ast.ImportFrom) else 'import '+','.join(a.name for a in n.names)
                for n in ast.walk(tree) if isinstance(n,(ast.Import,ast.ImportFrom))})
        else:
            row['syntax_parsed']=False
            row['inspection']='REA separately inventories the bridge; this Python inventory does not parse JavaScript.'
        rows.append(row)
    return {'kind':'tracked_application_source_inventory_not_complete_review','baseline_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
            'scope':'tracked rouge/**/*.py and rouge/**/*.cjs only, working-tree bytes; no private state or dependencies',
            'file_count':len(rows),'role_counts':dict(Counter(r['role'] for r in rows)),
            'application_review_complete':False,'limitations':['Static imports include conditional/test paths; dynamic imports and actual execution are not proven.','Syntax parsing/hashing does not review formulas, mechanics, UI, providers or dependencies.'],
            'files':rows}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=inventory();args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({k:result[k] for k in ('file_count','role_counts','application_review_complete')},ensure_ascii=False))
