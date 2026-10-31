from pathlib import Path
import json,subprocess,sys
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];B=R/'verification/maintenance/event-reader-layout-20261101';out=B/'native-final'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  p=subprocess.Popen([sys.executable,'-B','-X','utf8',str(Path(__file__)),'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':p.pid},flush=True);code=p.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':p.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'exit':code},flush=True);raise SystemExit(code)
from unittest.mock import patch
from copy import deepcopy
from hashlib import sha256
from PySide6.QtCore import Qt,QPoint
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QPushButton,QLabel
from PySide6.QtTest import QTest
from rouge import player_acceptance
from player_ui_verification import run

def check(section,window,gui,require):
 from rouge.current_vine_events_view import CurrentVineEventsDialog
 from rouge.current_resource_events_view import CurrentResourceEventsDialog
 from rouge.current_encounters_view import CurrentEncountersDialog
 from rouge.current_memory_tree_view import CurrentMemoryTreeDialog
 from rouge.current_exit_view import CurrentExitDialog
 from rouge.box_event_view import BoxEventDialog
 from rouge.current_resource_events import GOLD_EVENTS
 from rouge.player_map_reader import readable,make_reader
 from tests.test_current_vine_events_333 import by_original
 before=deepcopy(window.run.state);images=[];sizes=[];last=None
 cases=[('vine',lambda:CurrentVineEventsDialog('呼吸的红苔',parent=window),['controller','seeds']),('gold',lambda:CurrentVineEventsDialog('沉寂之屋',parent=window),['gold']),('black',lambda:CurrentEncountersDialog('黑诞',parent=window),['controller']),('resource',lambda:CurrentResourceEventsDialog(GOLD_EVENTS[0],parent=window),['gold']),('box',lambda:BoxEventDialog(parent=window),['covenant']),('exit',lambda:CurrentExitDialog(parent=window),['difficulty','action_points','gold']),('memory',lambda:CurrentMemoryTreeDialog(parent=window),['action_points','processed_parts','source_key','controller'])]
 for name,make,fields in cases:
  d=readable(make());d.show();gui.processEvents();p=d.panel;sizes.append({'case':name,'actual_size':[d.width(),d.height()]})
  require((d.width(),d.height())==(760,600),'events_'+name+'_actual_compact760x600')
  require(not p.conditions.isExpanded()and all(not getattr(p,n).isVisible()for n in fields),'events_'+name+'_only_existing_conditions_start_really_hidden')
  require(p.choices.wordWrap(),'events_'+name+'_choice_text_wraps')
  QTest.mouseClick(p.conditions.toggleButton(),Qt.MouseButton.LeftButton);QTest.qWait(20);gui.processEvents();require(p.conditions.isExpanded()and all(getattr(p,n).isVisible()for n in fields),'events_'+name+'_real_button_opens_all_local_controls')
  require(p.conditions.content().height()>0 and p.conditions.mapTo(p,QPoint()).y()+p.conditions.height()<=p.scene.y(),'events_'+name+'_expanded_controls_fit_above_scene_without_overlap')
  if name=='vine':
   p.choices.setCurrentRow(0);p.controller.setCurrentIndex(p.controller.findData(True));p.seeds.setValue(2);gui.processEvents();old=(p.scene_id,p.choice_id,p.player.toPlainText(),p.controller.currentData(),p.seeds.value());require(p.refresh_reference(),'events_vine_same_source_refresh_succeeds');gui.processEvents();require(p.conditions.isExpanded()and old==(p.scene_id,p.choice_id,p.player.toPlainText(),p.controller.currentData(),p.seeds.value()),'events_vine_refresh_preserves_values_choice_and_full_reading')
   p.heading_highlighter.rehighlight();require(any(f.format.fontWeight()==QFont.Weight.Bold for f in p.player.document().firstBlock().layout().formats()),'events_real_document_heading_bold_without_replacing_original')
   target=out/'vine-expanded.png';assert d.grab().save(str(target));images.append({'file':target.relative_to(R).as_posix(),'sha256':sha256(target.read_bytes()).hexdigest()})
  expanded=(p.scene.y(),p.tabs.height());p.conditions.toggleButton().setFocus();QTest.keyClick(p.conditions.toggleButton(),Qt.Key.Key_Space);QTest.qWait(20);gui.processEvents();require(not p.conditions.isExpanded()and all(not getattr(p,n).isVisible()for n in fields),'events_'+name+'_space_key_really_hides_controls')
  require(p.scene.y()<expanded[0]and p.tabs.height()>expanded[1],'events_'+name+'_settled_collapse_reclaims_actual_reading_height')
  if name=='vine':
   require(old==(p.scene_id,p.choice_id,p.player.toPlainText(),p.controller.currentData(),p.seeds.value()),'events_collapsing_never_discards_local_values_or_choice');target=out/'vine-collapsed.png';assert d.grab().save(str(target));images.append({'file':target.relative_to(R).as_posix(),'sha256':sha256(target.read_bytes()).hexdigest()})
   with patch('rouge.current_vine_events.reference',return_value=None):p.refresh_reference()
   require(p.result is None and not p.next_button.isEnabled()and p.technical.toPlainText()=='','events_source_loss_clears_old_text_links_and_result');p.refresh_reference();require(p.scene_id is None and p.choice_id is None,'events_source_recovery_requires_manual_scene_choice')
  if name=='memory':
   p.conditions.expand(False);gui.processEvents();p.choices.setCurrentRow(0);target=out/'memory-expanded.png';assert d.grab().save(str(target));images.append({'file':target.relative_to(R).as_posix(),'sha256':sha256(target.read_bytes()).hexdigest()})
  d.close();gui.processEvents();require(not d.isVisible(),'events_'+name+'_normal_close_is_effective');last=d
 catalog=window.node_catalog;window.centralWidget().setCurrentWidget(catalog);catalog.show_directory();gui.processEvents();index=next(i for i,row in enumerate(catalog.entries)if row['key']=='event:community_group_009');catalog.list.setCurrentRow(index);gui.processEvents();require(catalog.open_current_event_reference(),'events_existing_node_catalog_route_still_opens_exact_reader');d=catalog.current_reference_window;gui.processEvents();require(d.isVisible()and d.property('playerTheme')=='dark'and d.panel.event_id=='呼吸的红苔','events_catalog_route_has_same_dark_theme_and_exact_event');require(not d.panel.controller.isVisible(),'events_catalog_route_keeps_conditions_collapsed');record=catalog.entries[index]['record'];d.close()
 from rouge import player_map_reader
 with patch.object(player_map_reader,'readable',wraps=player_map_reader.readable)as wrapper:
  mapped=make_reader('event',record,window);require(mapped is not None and wrapper.call_count==1,'events_map_route_applies_external_theme_once')
 mapped.show();gui.processEvents();require(mapped.property('playerTheme')=='dark'and mapped.panel.event_id=='呼吸的红苔','events_map_and_catalog_reach_same_version_reader');mapped.panel.choices.setCurrentRow(0);target=out/'catalog-route.png';assert mapped.grab().save(str(target));images.append({'file':target.relative_to(R).as_posix(),'sha256':sha256(target.read_bytes()).hexdigest()});mapped.close()
 from rouge import current_event_directory as current_events
 from rouge.current_event_directory_view import make_event_dialog
 row=next(r for r in current_events.reference()['rows']if r['title']=='呼吸的红苔');target=current_events.resolve(current_events.reference(row['id']));extra=make_event_dialog(target,window);extra.show();gui.processEvents();require(extra.isVisible()and extra.property('playerTheme')=='dark'and extra.panel.scene_id==target['scene_id'],'events_full_current_directory_same_theme_and_exact_scene');extra.close()
 from types import SimpleNamespace
 from rouge.player_recent_scene import RecentScenePanel
 recent=RecentScenePanel(SimpleNamespace(state={'id':'public-native-theme','last_node_content':{'kind':'event','title':'呼吸的红苔'}}),parent=window);recent.event_choices.setCurrentIndex(1)
 with patch.object(player_map_reader,'readable',wraps=player_map_reader.readable)as wrapper:
  require(recent.open_event(),'events_recent_event_route_opens');require(wrapper.call_count==1,'events_recent_event_route_styles_once')
 gui.processEvents();require(recent.event_dialog.isVisible()and recent.event_dialog.property('playerTheme')=='dark','events_recent_event_dialog_visible_with_common_theme');recent.close()
 # Existing accurate branch to a fixed preview: no game transition or chat.
 from rouge.documented_event_flow_view import DocumentedEventFlowDialog
 d=readable(DocumentedEventFlowDialog('button',parent=window));d.show();p=d.panel;target=next(c for c in p.result['choices'].values()if len(c['stage_ids'])==1);p.scene.setCurrentIndex(p.scene.findData(target['scene_id']));p.choices.setCurrentRow(next(i for i in range(p.choices.count())if p.choices.item(i).data(Qt.ItemDataRole.UserRole)==target['id']));QTest.mouseClick(p.battle_button,Qt.MouseButton.LeftButton);gui.processEvents();child=p.battle_dialog;require(child is not None and child.isVisible()and child.panel.stage_id==target['stage_ids'][0],'events_existing_exact_battle_button_opens_correct_fixed_map');d.close();gui.processEvents();require(not child.isVisible(),'events_parent_close_also_closes_owned_battle_preview')
 last.show();last.panel.choices.setCurrentRow(0);gui.processEvents();window.player_validation_target=last;require(window.run.state==before,'events_all_reference_conditions_never_mutate_current_run')
 (out/'extra-images.json').write_text(json.dumps(images,indent=2)+'\n','utf8');(out/'actual-sizes.json').write_text(json.dumps(sizes,indent=2)+'\n','utf8')
with patch.object(player_acceptance,'check',check):raise SystemExit(run(447,out/'window.json'))
