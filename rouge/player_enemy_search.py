"""Literal source-description search, never inference of hidden enemy scripts."""
def matches(enemy,query):
    if not isinstance(enemy,dict)or not isinstance(query,str):return False
    needle=query.strip().casefold()
    parts=[enemy.get('name'),enemy.get('description'),*(enemy.get('abilities')or[])]
    return not needle or needle in'\n'.join(p for p in parts if isinstance(p,str)).casefold()
