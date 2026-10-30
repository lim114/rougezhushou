"""Find saved nodes without adding candidates or assigning an unbound title."""
def rows(graphs,query=''):
    from .player_map import node_style,zone_info
    from .map_reporting import location
    result=[];needle=query.strip().casefold()
    for zone,g in sorted(graphs.items(),key=lambda p:(zone_info(p[1])[1]or 99,p[0])):
        name,floor=zone_info(g)
        for n in g.get('nodes',[]):
            kind,note,_=node_style(n);titles=[]
            for content in [n.get('content'),*(n.get('content_history')or[])]:
                if isinstance(content,dict)and content.get('source')=='same_frame_selected_node'and isinstance(content.get('title'),str):titles.append(content['title'])
            title='、'.join(dict.fromkeys(titles));label=(f'第{floor}层 · 'if floor else'')+name+' · '+location(n,g['grid']['rows'])+' · '+(kind or'类型未确认')+' · '+note+(' · '+title if title else'')
            if not needle or needle in label.casefold():result.append({'key':(zone,g.get('template_id'),n['id']),'label':label})
    return result
