"""Resolve only a record's own content or a unique contemporaneous stored read."""
import math

def content_context(value):
    if not isinstance(value,dict):return None
    kind=value.get('kind')
    if kind not in ('battle','event'):return None
    title = value.get('title')
    if not isinstance(title, str) or not title.strip():return None
    context={'kind':kind,'title':title}
    for field in('stage_id','event_id','variant_id'):
        if field not in value:continue
        identity = value[field]
        if identity is not None and (not isinstance(identity, str) or not identity.strip()):return None
        context[field]=identity
    return context

def recorded_context(state,index):
    history=state.get('history');history=history if isinstance(history,list)else[]
    if type(index)is not int or not 0<=index<len(history):return None
    record=history[index]
    if not isinstance(record,dict):return None
    kind=record.get('kind')
    if kind=='map_node_content_confirmed':
        content=record.get('content')
        context=content_context(content)
        return context if context is not None and content.get('source')=='same_frame_selected_node' else None
    if kind!='node_content_seen':return None
    at=record.get('at')
    if type(at)not in(int,float)or not math.isfinite(at)or at<0:return None
    saved=state.get('node_contents')
    if not isinstance(saved, list):return None
    match = None
    title, location = record.get('title'), record.get('location')
    for content in saved:
        if not isinstance(content,dict):continue
        captured=content.get('captured_at')
        if type(captured)not in(int,float)or captured!=at or content.get('title')!=title:continue
        if content.get('location')!=location:continue
        context=content_context(content)
        if context is None:continue
        if match is not None and match != context:return None
        match = context
    return match
