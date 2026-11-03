"""Prepare only cache303 tools by retaining reviewed process gates, never execute them."""
import ast
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'.cache/p3-303-closeout'
HERE.mkdir(exist_ok=True)
source=(ROOT/'verification/sections/302-preparation/closeout-tools/close_section_302.py').read_text(encoding='utf8')
tree=ast.parse(source)
names=('require','path','rel','digest','load','encode','check_map','owned_process','original_window',
       'join_sources','visual_review','selected_window_sources','preparation_archive','necessary_attempt_history')
def convert(text):
    hashes=[]
    def save(match):
        hashes.append(match.group());return f'__PIN_{len(hashes)-1}__'
    text=re.sub(r'\b[0-9a-f]{64}\b|\b[0-9a-f]{40}\b',save,text)
    text=text.replace('303','__NEXT__').replace('302','303').replace('__NEXT__','304')
    for index,value in enumerate(hashes):text=text.replace(f'__PIN_{index}__',value)
    return text
common='\n\n'.join(convert(ast.get_source_segment(source,node))for name in names
    for node in tree.body if isinstance(node,ast.FunctionDef)and node.name==name)
(HERE/'reviewed-common.py.txt').write_text(common+'\n',encoding='utf8')
prefix='''"""Strict303 public closeout; preview by default, actual root-only --apply.
No tests/Qt/game/chat/private reads or Git mutation. Missing actual evidence fails.
"""
import argparse,ast,math,runpy
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from hashlib import sha256
import json,re,struct,subprocess
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())
HERE=ROOT/'.cache/p3-303-closeout'
PARENT='c2b78e4aa4136fe739067b5ccf9d13b595142320'
TITLE='畸症与本性难移固定原图的49格独立直接参考'
CANONICAL='scripts/verify_direct_map_window_303.py'
PACKET='research/p3-map-direct-ground-303'
MANIFEST=PACKET+'/source-manifest.json'
DATA='rouge/data/fixed-landmark-references.json'
REGULAR='rouge/data/battle-map-projections.json'
BUILDER='scripts/extend_direct_landmark_303.py'
COMPARISON=PACKET+'/build-receipt.json'
MANIFEST_SHA='e1ad287b4d4c2879e7fbad16b60b825db660147c2ba0a719dde60b7cfea6e2c4'
DATA_SHA='dc43bbbe70eab6f11cc8661c3bfeab994000ea614ea0f8c999a596f5cb2c445a'
COMPARISON_SHA='93f1d1db4ea633a32a720d650ff513592294ba82a61db3ec9cf10d9f70ecdaad'
FULL='verification/full-290/summary.json';FULL_SHA='2c6e93534e443089bc0f8ffbbd686e3c37610ccf3c4aafd43fbf44d16188b823'
CHANGED_EXISTING={DATA}
MAINTENANCE={
 'tests/test_direct_landmark_294.py':'263cea49f3f19514a5fb6be72a3dc42926ba4cab6007bbc14d21a489a07c1f52',
 'tests/test_map_projection_048.py':'b2454d2c5c53a3b81164cce528f6dcd5c9f99aa2b0a3027b721e23aa50e145de'}
PROGRESS_SHA_BEFORE='111962b1622515c494ae81a06ac19b915db797211e926165a9947b80fade8a0b'
OLD_PROGRESS='其中10图/18关已有58格直接参考，整图仍未校准'
NEW_PROGRESS='其中12图/21关已有107格直接参考，整图仍未校准'
'''
body=(HERE/'303-body.py.txt').read_text(encoding='utf8')
target=HERE/'close_section_303.py'
target.write_text(prefix+'\n'+common+'\n\n'+body,encoding='utf8')
compile(target.read_bytes(),str(target),'exec')
print('Prepared and compiled cache-only303 helper; no producer or test executed.')
