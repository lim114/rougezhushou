"""Manual notebook hierarchy, bound to the same public reference as exact notes."""
import json
from .player_notes import content_key
from .current_stage_directory import FLOORS


def source(rows):
    return json.loads(rows[0]['context']['variant_id'])[0] if rows else None


def scope(rows, floor=None, node=None):
    if not rows:return None
    title='黑流树海'
    if floor is not None:title+=' · '+dict(FLOORS)[floor]
    if node is not None:title+=' · '+node
    identity=json.dumps([source(rows),floor,node],ensure_ascii=True,separators=(',',':'))
    return {'kind':'note-scope','title':title,'variant_id':identity}


def scope_parts(content, rows):
    if not rows or content.get('kind')!='note-scope':return None
    try:
        version,floor,node=json.loads(content['variant_id'])
        if version!=source(rows)or floor not in dict(FLOORS):return None
        if node is not None and node not in {n for r in rows for n in r['nodes']}:return None
        if scope(rows,floor,node)!=content:return None
        return floor,node
    except(ValueError,TypeError,KeyError):return None


def parents(content, rows, floor=None, node=None):
    """Only known/manual scope, never infer a live scene's floor from its title."""
    if not content or not rows:return []
    if content.get('kind')=='note-scope':
        parts=scope_parts(content,rows)
        if parts is None:return []
        floor,node=parts
    else:
        row=next((r for r in rows if content_key(r['context'])==content_key(content)),None)
        if row is None:return []
        floor=floor if floor in row['floors'] else row['floors'][0] if len(row['floors'])==1 else None
        node=node if node in row['nodes'] else row['nodes'][0] if len(row['nodes'])==1 else None
    candidates=[scope(rows)]
    if floor is not None:candidates.append(scope(rows,floor))
    if node is not None:candidates.append(scope(rows,floor,node))
    return [c for c in candidates if content_key(c)!=content_key(content)]
