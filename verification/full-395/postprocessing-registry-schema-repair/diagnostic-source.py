"""Readonly diagnosis of a refused post-processing provenance edge."""
from pathlib import Path
import importlib.util,json,inspect
R=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())
path=R/'.cache/full395-post/seal_summary395.py';spec=importlib.util.spec_from_file_location('sealer395_diagnostic',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.ATTEMPT=2;module.FREEZE_SHA='bf83e26f3cfdec95159858cadf12d5429fdc37371a491715af6e632d3e7ed485';module.ARCHIVE=R/'verification/full-395/execution-attempt2';module.VISUAL=R/'verification/full-395/root-visual-review.json'
original=module.require
def require(value,message):
    if not value:
        local=inspect.currentframe().f_back.f_locals
        print(json.dumps({'message':message,'function':inspect.currentframe().f_back.f_code.co_name,'index':local.get('index'),'origin':local.get('origin'),'chain_item':local.get('item'),'raw_leaf_row':local.get('row')},ensure_ascii=True,default=str))
    return original(value,message)
module.require=require
manifest=json.loads((module.ARCHIVE/'archive-manifest.json').read_bytes())
module.verify_visual('34a8f7f32a5623a7d931ad0718056f5dcd88b58aedd4e691329a841782159efe',manifest['files'],'3c7fb3e70fca3c892558c1fe74182fcf41a968b9528572e7a23f6ab49044172f')
