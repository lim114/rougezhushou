"""Per-node identities and generation budgets at the RunState public seam."""
import copy
from pathlib import Path
import tempfile
import unittest
import cv2
import numpy as np
from rouge.recognition import ScreenReader
from rouge.run_state import RunState
from tests.test_map_templates import first_map
from rouge.map_recognition import map_data


def source_graph(template_id, hidden_node):
    template=next(t for t in map_data()['templates'] if t['id']==template_id)
    return {'status':'matched','zone_id':template['zone_id'],'template_id':template_id,
        'edges':template['edges'],'current_node':None,'difficulty_value':None,
        'grid':{'rows':template['rows'],'cols':template['cols']},'source':map_data()['source'],
        'nodes':[{**n,'template_type':n['fixed_type'],'observed_type':'未知的诡秘' if n['id']==hidden_node else None,
                  'center':[.1+n['col']*.1,.1+n['row']*.1],'visible':n['id']==hidden_node,'prediction':None}
                 for n in template['nodes']]}


class NodeContentTests(unittest.TestCase):
    def test_legacy_clearing_record_recovers_only_confirmed_same_layout_history(self):
        import json
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory)/'run.json';run=RunState(file);at=run.state['started_at']+1
            graph=source_graph('2a','0,1')
            next(n for n in graph['nodes'] if n['id']=='1,1')['observed_type']='诡意行商'
            run.apply({'map':graph},at)
            legacy=json.loads(file.read_text(encoding='utf8'))
            node=next(n for n in legacy['maps']['zone_2']['nodes'] if n['id']=='1,1')
            node['observed_type']=node['remembered_type']='林间空地'
            legacy['history'].append({'at':at+1,'kind':'map_node_revealed','zone_id':'zone_2',
                                      'node_id':'1,1','previous':'诡意行商','type':'林间空地'})
            file.write_text(json.dumps(legacy),encoding='utf8')
            restored=RunState(file)
            self.assertEqual(next(n for n in restored.state['maps']['zone_2']['nodes'] if n['id']=='1,1')['remembered_type'],'诡意行商')
            self.assertEqual(restored.state['maps']['zone_2']['generation_budget']['诡意行商']['known_total'],1)

    def test_passed_clearing_keeps_original_type_and_consumes_generation_budget_after_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory)/'run.json';run=RunState(file);at=run.state['started_at']+1
            graph=source_graph('2a','0,1')
            for node in graph['nodes']:
                if node['id'] in ('1,1','2,1'):node['observed_type']='诡意行商'
            run.apply({'map':graph},at)
            passed=copy.deepcopy(graph)
            for node in passed['nodes']:
                if node['id'] in ('1,1','2,1'):node['observed_type']='林间空地'
            run.apply({'map':passed},at+1)
            run=RunState(file)
            run.apply({'map':passed},at+2)
            saved=run.state['maps']['zone_2']
            self.assertEqual(saved['generation_budget']['诡意行商']['known_total'],2)
            self.assertEqual(saved['generation_budget']['诡意行商']['remaining_capacity'],0)
            self.assertNotIn('诡意行商',next(n for n in saved['nodes'] if n['id']=='0,1')['prediction']['candidates'])
            node=next(n for n in saved['nodes'] if n['id']=='1,1')
            self.assertEqual(node['observed_type'],'林间空地')
            self.assertEqual(node['remembered_type'],'诡意行商')

    def test_fog_next_to_visible_vantage_point_reports_visibility_conflict(self):
        with tempfile.TemporaryDirectory() as directory:
            run=RunState(Path(directory)/'run.json');at=run.state['started_at']+1
            graph=source_graph('2a','0,1')
            next(n for n in graph['nodes'] if n['id']=='0,0')['observed_type']='羽瞰点'
            run.apply({'map':graph},at)
            saved=run.state['maps']['zone_2'];node=next(n for n in saved['nodes'] if n['id']=='0,1')
            self.assertEqual(node['prediction']['status'],'conflict')
            self.assertIn('0,1',saved['reveal_range_conflicts'])

    def test_immediately_revealed_nodes_are_not_fog_candidates_on_later_floors(self):
        with tempfile.TemporaryDirectory() as directory:
            run=RunState(Path(directory)/'run.json');at=run.state['started_at']+1
            for template,node_id in [('2a','0,1'),('3a','0,1'),('5a','0,1')]:
                run.apply({'map':source_graph(template,node_id)},at)
                graph=run.state['maps']['zone_'+template[0]]
                node=next(n for n in graph['nodes'] if n['id']==node_id)
                self.assertNotIn('羽瞰点',node['prediction']['candidates'])
                self.assertNotIn('曲折密道',node['prediction']['candidates'])
                if template=='5a':self.assertNotIn('命运所指',node['prediction']['candidates'])
                at+=1

    def test_fixed_and_revealed_same_slot_count_once_and_exhaust_type_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            run=RunState(Path(directory)/'run.json');at=run.state['started_at']+1
            evidence=copy.deepcopy(first_map()['run'])
            for node in evidence['map']['nodes']:
                if node['id']=='1,3':node['observed_type']='诡意行商'
                if node['id']=='0,1':node['observed_type']='紧急作战'
            run.apply(evidence,at)
            graph=run.state['maps']['zone_1'];budget=graph['generation_budget']
            self.assertEqual(budget['诡意行商']['known_total'],1)
            self.assertEqual(budget['紧急作战']['remaining_capacity'],0)
            other=next(n for n in graph['nodes'] if n['id']=='0,3')
            self.assertNotIn('紧急作战',other['prediction']['candidates'])

    def test_event_same_title_and_description_preserve_ambiguous_scene_ids(self):
        import os
        os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QImage, QPainter, QFont, QFontDatabase, QColor
        app=QApplication.instance() or QApplication([])
        font_file=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts/msyh.ttc'
        font_id=QFontDatabase.addApplicationFont(str(font_file));families=QFontDatabase.applicationFontFamilies(font_id)
        if families:
            font_family=families[0]
        else:
            # This synthetic OCR fixture needs a real CJK font. Keep the native
            # font first; an explicit portable font never impersonates msyh.
            configured_font=os.environ.get('ROUGE_TEST_CJK_FONT')
            if not configured_font:
                raise RuntimeError('CJK font fixture unavailable: '+str(font_file)+
                    '; set ROUGE_TEST_CJK_FONT to a real font file containing Noto Sans CJK SC.')
            fallback_file=Path(configured_font)
            if not fallback_file.is_file():
                raise RuntimeError('Configured CJK font fixture file is unavailable: '+str(fallback_file))
            fallback_id=QFontDatabase.addApplicationFont(str(fallback_file))
            fallback_families=QFontDatabase.applicationFontFamilies(fallback_id)
            if 'Noto Sans CJK SC' not in fallback_families:
                raise RuntimeError('Configured CJK font fixture has no usable Noto Sans CJK SC family: '+str(fallback_file))
            font_family='Noto Sans CJK SC'
        from rouge.node_events import event_data
        scene=event_data()['scenes']['scene_ro6_wish_2']
        image=QImage(1280,720,QImage.Format.Format_RGB888);image.fill(QColor('#101820'))
        painter=QPainter(image);painter.setPen(QColor('white'));painter.setFont(QFont(font_family,24))
        painter.drawText(90,100,'无人商店')
        prose=scene['description']
        for i in range(0,len(prose),26):painter.drawText(90,180+(i//26)*55,prose[i:i+26])
        painter.end()
        array=np.frombuffer(image.bits(),dtype=np.uint8).reshape(720,image.bytesPerLine())[:,:1280*3].reshape(720,1280,3)[:,:,::-1].copy()
        observed=ScreenReader().read(array)
        content=observed['node_content']
        self.assertEqual(content['title'],'无人商店')
        self.assertEqual(content['identity_status'],'ambiguous_scene')
        self.assertEqual(set(content['scene_candidates']),{'scene_ro6_wish_2','scene_ro6_wish_3'})
        self.assertIsNone(content['node_type'])
        self.assertEqual(observed['page'],'node_event')
        with tempfile.TemporaryDirectory() as directory:
            run=RunState(Path(directory)/'run.json');at=run.state['started_at']+1
            run.apply(observed['run'],at)
            run.apply(observed['run'],at+1)
            self.assertEqual(len(run.state['node_contents']),1)
            self.assertIsNone(run.state['last_node_content']['location'])

    def test_confirmed_low_difficulty_rejects_fog_on_template_exit(self):
        with tempfile.TemporaryDirectory() as directory:
            run=RunState(Path(directory)/'run.json');at=run.state['started_at']+1
            evidence=copy.deepcopy(first_map()['run'])
            evidence['config']['difficulty']={'value':0,'source':'controlled_visible_config'}
            evidence['map']['difficulty_value']=None
            run.apply(evidence,at)
            graph=run.state['maps']['zone_1']
            node=next(n for n in graph['nodes'] if n['id']=='2,4')
            self.assertEqual(node['prediction']['status'],'conflict')
            self.assertEqual(node['prediction']['candidates'],[])

    def test_visible_selected_battle_binds_stage_to_selection_not_current_position(self):
        root=Path(__file__).resolve().parents[1]
        image=cv2.imdecode(np.fromfile(root/'samples/native-client/map-template-node-detail.png',np.uint8),1)
        observed=ScreenReader().read(image,client_rect=[2,45,2050,1125])
        self.assertEqual(observed['map']['template_id'],'1c')
        self.assertEqual(observed['map']['selected_node'],'0,2')
        self.assertEqual(observed['map']['current_node'],'1,2')
        nodes={n['id']:n for n in observed['map']['nodes']}
        self.assertEqual(nodes['0,2']['content']['title'],'遗忘时间')
        self.assertNotIn('content',nodes['1,2'])
        from rouge.map_reporting import format_node
        detail=format_node(observed['map'],'0,2')
        self.assertIn('宝箱生成候选',detail)
        self.assertIn('恶笼草',detail)
        self.assertIn('概率未核验',detail)
        self.assertNotIn('奖励资料参考',format_node(observed['map'],'1,2'))

    def test_fixed_first_floor_merchants_do_not_create_extra_random_merchants(self):
        with tempfile.TemporaryDirectory() as directory:
            run=RunState(Path(directory)/'run.json');at=run.state['started_at']+1
            evidence=copy.deepcopy(first_map()['run'])
            next(n for n in evidence['map']['nodes'] if n['id']=='0,1')['observed_type']='未知的诡秘'
            run.apply(evidence,at)
            graph=run.state['maps']['zone_1'];node=next(n for n in graph['nodes'] if n['id']=='0,1')
            self.assertNotIn('诡意行商',node['prediction']['candidates'])
            self.assertEqual(graph['generation_budget']['诡意行商']['fixed'],1)
            self.assertFalse(graph['generation_budget']['诡意行商']['random_eligible'])

    def test_two_battle_nodes_keep_different_stage_titles_across_fog_and_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory)/'run.json';run=RunState(file);at=run.state['started_at']+1
            evidence=copy.deepcopy(first_map()['run'])
            for node in evidence['map']['nodes']:
                if node['id'] in ('0,1','1,1'):
                    node['observed_type']='作战'
                    node['content']={'kind':'battle','title':'遗忘时间' if node['id']=='1,1' else '火树灵',
                        'identity_status':'visible_title','node_type':'作战','source':'same_frame_selected_node',
                        'variants':[], 'probability':None}
            run.apply(evidence,at)
            run.apply(copy.deepcopy(first_map()['run']),at+1)
            saved=RunState(file)
            nodes={n['id']:n for n in saved.state['maps']['zone_1']['nodes']}
            self.assertEqual(nodes['1,1']['remembered_content']['title'],'遗忘时间')
            self.assertEqual(nodes['0,1']['remembered_content']['title'],'火树灵')
            self.assertNotIn('remembered_content',nodes['2,1'])
            self.assertEqual(len([h for h in saved.state['history'] if h['kind']=='map_node_content_confirmed']),2)
            saved.reset();self.assertEqual(saved.state['maps'],{})


if __name__=='__main__':unittest.main()
