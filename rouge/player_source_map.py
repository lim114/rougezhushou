"""Only explicit public node enum/name pairs may navigate the read-only map."""
PAIRS={'BATTLE_NORMAL':'作战','BATTLE_ELITE':'紧急作战','BATTLE_BOSS':'险路恶敌','BATTLE_SAVAGE':'“居民”据点','EVACUATE':'险路小径','FINAL':'险路尽头','SCRAP_SHOP':'秘境行商'}

def targets(index,version,identity,pool_id):
    from .player_item_sources import selected_pool
    return pool_targets(selected_pool(index, version, identity, pool_id))


def pool_targets(pool):
    if pool is None:
        return []
    result=[]
    for row in pool.get('nodeBindings') or []:
        if not isinstance(row,dict):continue
        kind=PAIRS.get(row.get('nodeType'))
        if kind and row.get('nodeName')==kind and kind not in result:result.append(kind)
    return result

def companion(widget):
    while widget is not None:
        if hasattr(widget,'open_map')and hasattr(widget,'map_popup'):return widget
        value=getattr(widget,'compact_window',None)
        if value is not None:return value
        widget=widget.parentWidget()
    return None
