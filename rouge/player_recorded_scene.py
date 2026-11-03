"""Resolve only a record's own content or a unique contemporaneous stored read."""
from copy import deepcopy
import math

def content_context(value):
    if not isinstance(value,dict)or value.get('kind')not in('battle','event'):return None
    if not isinstance(value.get('title'),str)or not value['title'].strip():return None
    for field in('stage_id','event_id','variant_id'):
        if field in value and value[field]is not None and(not isinstance(value[field],str)or not value[field].strip()):return None
    return deepcopy({k:value[k]for k in('kind','title','stage_id','event_id','variant_id')if k in value})

def recorded_context(state,index):
    history=state.get('history');history=history if isinstance(history,list)else[]
    if type(index)is not int or not 0<=index<len(history):return None
    record=history[index]
    if not isinstance(record,dict):return None
    if record.get('kind')=='map_node_content_confirmed':
        content=record.get('content')
        return content_context(content)if isinstance(content,dict)and content.get('source')=='same_frame_selected_node'else None
    if record.get('kind')!='node_content_seen':return None
    at=record.get('at')
    if type(at)not in(int,float)or not math.isfinite(at)or at<0:return None
    saved=state.get('node_contents');saved=saved if isinstance(saved,list)else[];matches=[]
    for content in saved:
        if not isinstance(content,dict):continue
        captured=content.get('captured_at')
        if type(captured)not in(int,float)or captured!=at or content.get('title')!=record.get('title'):continue
        if content.get('location')!=record.get('location'):continue
        context=content_context(content)
        if context is not None and context not in matches:matches.append(context)
    return matches[0]if len(matches)==1 else None
