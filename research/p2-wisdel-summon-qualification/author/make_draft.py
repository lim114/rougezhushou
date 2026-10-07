from pathlib import Path
p=Path(__file__).resolve().parent
q=p/'draft/rouge/operator_engine.py';b=q.read_bytes();marker=b"            if wisdel_s1_unresolved:result['complete']=False;result['estimate']['complete']=False\r\n";assert b.count(marker)==1
addition=b"            from .wisdel_summon_qualification import reference as summon_qualification_reference\r\n            result['wisdel_summon_qualification_reference']=summon_qualification_reference(self.p,self.s)\r\n"
q.write_bytes(b.replace(marker,marker+addition))
q=p/'draft/rouge/reporting.py';s=q.read_text();marker="    wisdel=result.get('wisdel_secondary_reference')\n";assert s.count(marker)==1
addition="""    summon_routes=result.get('wisdel_summon_qualification_reference')
    if summon_routes:
        talent=summon_routes['talent_route'];route=summon_routes['skill_route']
        status=lambda path:'已达原表培养门槛' if path['cultivation_qualified'] else '未达原表培养门槛'
        source=route['selected_level_source']
        skill_text=(readable_description(source['description'],source['values']) if source else
                    '…'.join(route['original_common_fragments']))
        sections.append(section('wisdel_summon_qualification','魂灵之影 · 本体召唤途径培养资料',[
            metric('talent_qualification',talent['name']+' · 精二1级门槛',status(talent)),
            metric('s3_qualification','第三技能 · 精二1级门槛',status(route)),
            metric('s3_selected','当前是否选中第三技能','是' if route['currently_selected'] else '否')],
            ['第二天赋原文：'+readable_description(talent['description'],{}),
             ('当前第三技能原文：' if source else '第三技能各级原文共通部分（省略数量）：')+skill_text,
             '以上仅列固定原表第二天赋与第三技能两条本体途径的培养资格，不表示实际召唤、当前存在或已完成施放。',
             '魂灵数量与施放次数仍是窗口来源声明，未确定其来源归属；本资料不涵盖模组或藏品可能附着的全部途径。',
             '实际来源、存活和施放时钟仍待核验；未改变指定次数的条件参考。']))
"""
q.write_text(s.replace(marker,addition+marker))
print('external source-only engine/reference/report edits complete')
