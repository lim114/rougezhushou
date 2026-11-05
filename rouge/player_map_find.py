"""One current projection for saved-node coverage and search."""
class NodeFinder:
    def __init__(self,graphs):
        from .player_map import node_style,zone_info
        from .map_reporting import location
        self.entries=[];self.counts={k:0 for k in('read','fixed','unknown')}
        zones=[(zone,g,*zone_info(g))for zone,g in graphs.items()]
        for zone,g,name,floor in sorted(zones,key=lambda row:(row[3]or 99,row[0])):
            for n in g.get('nodes',[]):
                kind,note,origin=node_style(n);category='read'if origin in('observed','history')else'fixed'if origin=='template'else'unknown';titles=[]
                self.counts[category]+=1
                for content in [n.get('content'),n.get('remembered_content'),*(n.get('content_history')or[])]:
                    if isinstance(content,dict)and content.get('source')=='same_frame_selected_node'and isinstance(content.get('title'),str):titles.append(content['title'])
                title='、'.join(dict.fromkeys(titles));label=(f'第{floor}层 · 'if floor else'')+name+' · '+location(n,g['grid']['rows'])+' · '+(kind or'类型未确认')+' · '+note+(' · '+title if title else'')
                self.entries.append({'key':(zone,g.get('template_id'),n['id']),'label':label,'evidence':category})

    def find(self,query='',evidence=None):
        needle=query.strip().casefold()
        return [row for row in self.entries if(not evidence or row['evidence']==evidence)and(not needle or needle in row['label'].casefold())]
