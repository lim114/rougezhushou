"""CACHE DRAFT: four fixed-map references, three actual sizes per stage.

Never execute this draft. Root must bind the final source receipt/manifest,
promote the canonical script and freeze sources before one owned native run.
"""
import argparse
from contextlib import ExitStack
from copy import deepcopy
from datetime import datetime,timezone
import hashlib,json,math,os
from pathlib import Path
import sys,tempfile,traceback
from unittest.mock import patch

ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())
sys.path.insert(0,str(ROOT))
CANONICAL='scripts/verify_direct_map_window_294_full320.py'
PACKET='research/p3-map-direct-checkpoints-294'
MANIFEST_SHA256='52e447bc1c616db021da9cad9c2cbc68a0a63849138cd7f9297b4ccc1b32c097'
COMPARISON='research/p3-map-direct-checkpoints-294/build-receipt.json'
COMPARISON_SHA256='25947432426d55cdae03ad126b32738c60d4a7650f6201250346da6ef0f8f8b9'
STAGES=('ro6_n_3_2','ro6_e_3_2','ro6_t_5','ro6_e_t_5')
SIZES=((1280,850),(1440,900),(1520,940))

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_bytes())

def source_contract():
    # Full320 retains every old source/UI assertion; independently rebuild all67 later308 requests too.
    from scripts import extend_direct_landmark_308 as extension
    expected_current, current_comparison = extension.build()
    if read(ROOT/'rouge/data/fixed-landmark-references.json') != expected_current:
        raise ValueError('Current123 data differs from complete original308 build.')
    if current_comparison['new_requested_points'] != 67:
        raise ValueError('All67 later source requests are required.')
    if MANIFEST_SHA256.startswith('PENDING') or COMPARISON_SHA256.startswith('PENDING'):
        raise RuntimeError('Final author source packet and actual comparison receipt are not bound.')
    folder=ROOT/PACKET;manifest_path=folder/'source-manifest.json'
    if sha(manifest_path)!=MANIFEST_SHA256:raise ValueError('Frozen public source manifest changed.')
    manifest=read(manifest_path)
    for name,expected in manifest['files'].items():
        if Path(name).name!=name:raise ValueError('Source packet paths must be exact flat original names.')
        path=folder/name
        if sha(path)!=expected['sha256'] or path.stat().st_size!=expected['bytes']:
            raise ValueError('Frozen public source member changed: '+name)
    if sha(ROOT/COMPARISON)!=COMPARISON_SHA256:raise ValueError('Actual public comparison receipt changed.')
    comparison=read(ROOT/COMPARISON)
    runtime=read(ROOT/'rouge/data/fixed-landmark-references.json')
    #305: current107 dataset must preserve the complete original58 records;
    # the old18 accepted source observations and every UI assertion stay intact.
    if sha(ROOT/'rouge/data/fixed-landmark-references.json')!='7e8044bcbdb5cf9605152f55fa2d262336e19bbf5fc74f8a8b9352f2a6fc1dde':
        raise ValueError('Reviewed current107 direct dataset changed.')
    old58_path=ROOT/'research/p3-map-direct-ground-303/prior-direct-references.json'
    if sha(old58_path)!=comparison['output_sha256'] or comparison['output_sha256']!='63ec9488f8f905d2ced1a4e349413e9c92d78125b9f1c94c00293cafa4d348f5':
        raise ValueError('Original compared58 complete output authority changed.')
    old58=read(old58_path)
    if any(runtime[group].get(key)!=value for group in('references','stages')for key,value in old58[group].items()):
        raise ValueError('Original58 full records changed in current107 dataset.')
    accepted=[row for row in comparison['new_agreement_comparisons'] if row['accepted_for_runtime'] is True]
    if comparison['new_accepted_points']!=len(accepted):raise ValueError('Comparison count differs from actual accepted rows.')
    points={}
    for sid in STAGES:
        reference=runtime['stages'][sid]['reference']
        rows=[row for row in accepted if row['reference']==reference]
        expected=tuple((row['row'],row['col'],*row['observed_pixel'])for row in rows)
        actual=tuple((row['row'],row['col'],*row['observed_pixel'])for row in runtime['references'][reference]['points'])
        if not expected or actual!=expected:raise ValueError('Runtime points differ from accepted frozen source rows: '+sid)
        points[sid]=expected
    prior=read(folder/'prior-direct-references.json')
    for group in ('references','stages'):
        if not all(runtime[group].get(key)==value for key,value in prior[group].items()):
            raise ValueError('Prior direct-reference values changed.')
    prior_counts=(len(prior['references']),len(prior['stages']),sum(len(row['points'])for row in prior['references'].values()))
    if prior_counts!=(8,14,40):raise ValueError('Prior direct scope differs from its actual frozen inputs.')
    regular=read(ROOT/'rouge/data/battle-map-projections.json')
    if regular!=read(folder/'prior-regular-projections.json')or(len(regular['calibrations']),len(regular['stages']))!=(12,24):
        raise ValueError('Existing regular calibration dictionaries/scope changed.')
    stages=read(ROOT/'rouge/data/battle-previews.json')['stages']
    incomplete={key:value for key,value in stages.items()if key not in regular['stages']}
    if(len(incomplete),len({value['image']['sha256']for value in incomplete.values()}))!=(81,59):
        raise ValueError('Whole-map calibration gaps were silently reclassified.')
    return {'comparison':comparison,'points':points,'runtime':runtime,'prior_direct_points_preserved':40,
        'regular_images_preserved':12,'regular_stages_preserved':24,'remaining_full_map_stages':81,'remaining_full_map_images':59}

def bound_files():
    from scripts import extend_direct_landmark_308 as extension
    extension_inputs=set(extension.source_inputs()['files']) | {'scripts/extend_direct_landmark_308.py','research/p3-map-direct-ground-308/source-manifest.json'}
    names={CANONICAL,'research/p3-map-direct-ground-303/prior-direct-references.json','rouge/app.py','rouge/battle_preview.py','rouge/battle_view.py',
        'rouge/map_projection.py','rouge/fixed_landmark_mapping.py','rouge/player_tile_information.py',
        'rouge/branch_choice.py','rouge/branch_reference_view.py','rouge/spawn_reference.py','rouge/ui_state.py',
        'rouge/data/battle-previews.json','rouge/data/fixed-landmark-references.json',
        'rouge/data/battle-map-projections.json','scripts/extend_direct_landmark_294.py',
        'tests/test_direct_landmark_294.py',COMPARISON}
    names.update(extension_inputs)
    folder=ROOT/PACKET
    if not folder.is_dir():raise FileNotFoundError('Final public packet is not present.')
    for path in folder.rglob('*'):
        if path.is_symlink():raise ValueError('Source packet symlink is not permitted.')
        if path.is_file():names.add(path.relative_to(ROOT).as_posix())
    stages=read(ROOT/'rouge/data/battle-previews.json')['stages']
    for sid in STAGES:names.add('rouge/data/'+stages[sid]['image']['file'])
    result={}
    for name in sorted(names):
        path=ROOT/name
        if not path.is_file()or path.is_symlink()or not path.resolve().is_relative_to(ROOT):
            raise ValueError('Selected source is not a public regular project file: '+name)
        result[name]=sha(path)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt',required=True);parser.add_argument('--visible-ms',type=int,default=120000)
    args=parser.parse_args();destination=Path(args.receipt).resolve()
    if destination.exists():raise FileExistsError('Preserve the first actual receipt.')
    if args.visible_ms<=0:raise ValueError('Positive --visible-ms required.')
    destination.parent.mkdir(parents=True,exist_ok=True)
    images={sid:destination.with_name(destination.stem+'-'+sid+'.png')for sid in STAGES}
    if any(path.exists()for path in images.values()):raise FileExistsError('Preserve first actual images.')
    started=datetime.now(timezone.utc).isoformat()
    before={};after={};checks=[];observations=[];failure=None;done=False;closed=False
    qpa=None;qt_exit=None;executions=0;contract=None
    attempts={name:0 for name in ('game_enumeration','game_connect','game_capture','game_next_frame',
        'desktop_start','desktop_request','provider_chat','credential_read')}
    def require(value,label):
        nonlocal executions
        if not value:raise AssertionError(label)
        executions+=1
        if label not in checks:checks.append(label)
    def forbidden(name):
        def blocked(*_,**__):
            attempts[name]+=1;raise AssertionError('Forbidden original external entry: '+name)
        return blocked
    try:
        if sys.platform!='win32':raise RuntimeError('Actual native Windows required.')
        if Path(__file__).resolve()!=(ROOT/CANONICAL).resolve():raise RuntimeError('Cache draft must not be executed.')
        contract=source_contract();before=bound_files()
        from PySide6.QtCore import Qt,QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        from PySide6.QtTest import QTest
        import win32gui,win32process
        from rouge import app as app_module
        from rouge.battle_preview import battle_data
        from rouge.branch_choice import OVERVIEW
        gui=QApplication([]);qpa=gui.platformName()
        require(qpa=='windows','actual_native_windows_QPA')
        class PublicWindow(app_module.MainWindow):
            def refresh_windows(self):self.windows.clear()
        with tempfile.TemporaryDirectory(prefix='rouge-294-direct-map-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for key,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json',
                'OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():
                stack.enter_context(patch.object(app_module,key,value))
            stack.enter_context(patch.object(app_module,'list_game_windows',side_effect=forbidden('game_enumeration')))
            for method,name in [('connect','game_connect'),('capture','game_capture'),('next_frame','game_next_frame')]:
                stack.enter_context(patch.object(app_module.GameCapture,method,side_effect=forbidden(name)))
            for method,name in [('start','desktop_start'),('request','desktop_request')]:
                stack.enter_context(patch.object(app_module.DesktopBackend,method,side_effect=forbidden(name)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')))
            stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=PublicWindow();window.setWindowTitle('第294节 · 两图已核地格与途经点（公开隔离验收）')
            window.resize(*SIZES[0]);window.show()
            panel=window.battle_preview;tabs=window.centralWidget();initial_run=deepcopy(window.run.state)
            stage_number=0;size_number=0;state={};emissions=[];inverse_emissions=[]
            panel.grid.cellSelected.connect(lambda value:emissions.append(deepcopy(value)))
            panel.original.cellSelected.connect(lambda value:inverse_emissions.append(deepcopy(value)))
            def isolated():
                require(not window.auto.isChecked()and not window.timer.isActive(),'automatic_sampling_and_timer_disabled')
                require(window.capture.target is None and window.desktop.process is None,'capture_target_and_desktop_backend_inactive')
                require(all(value==0 for value in attempts.values()),'all_eight_external_operation_attempts_zero')
            def native():
                hwnd=int(window.winId());thread,pid=win32process.GetWindowThreadProcessId(hwnd)
                require(win32gui.IsWindow(hwnd)and win32gui.IsWindowVisible(hwnd)and window.isVisible(),'actual_owned_native_HWND_visible')
                require(pid==os.getpid()and not win32gui.IsIconic(hwnd),'actual_HWND_owned_by_fixture_and_not_minimized')
                actual=[window.width(),window.height()]
                require(actual==list(SIZES[size_number]),'actual_logical_client_size_equals_requested')
                return {'hwnd':hwnd,'process_id':pid,'thread_id':thread,'qpa':qpa,'client_size':actual}
            def reader(widget):
                cursor=widget.textCursor()
                return {'text_sha256':hashlib.sha256(widget.toPlainText().encode()).hexdigest(),
                    'anchor':cursor.anchor(),'position':cursor.position(),'selected':cursor.selectedText(),
                    'vertical':widget.verticalScrollBar().value(),'horizontal':widget.horizontalScrollBar().value()}
            def selection(include_viewport=True):
                value={'main_tab':tabs.currentIndex(),'stage':panel.current_stage,
                    'stage_branch':panel.stage_choices.branch.currentData(),'stage_choice':panel.stage_combo.currentData(),
                    'wave':panel.wave_combo.currentData(),'enemy_branch':panel.enemy_choices.branch.currentData(),
                    'enemy':deepcopy(panel.enemy_combo.currentData()),'include_branches':panel.include_branches.isChecked(),
                    'technical':panel.technical.isChecked(),'detail_key':deepcopy(panel._detail_key),
                    'tile':deepcopy(panel._tile_cell),'row':deepcopy(panel.original.selected['id']if panel.original.selected else None),
                    'ordinal':panel.occurrence.value(),'spawn':reader(panel.spawn_detail),'enemy_text':reader(panel.enemy_detail)}
                if not include_viewport:
                    for name in ('spawn','enemy_text'):
                        value[name].pop('vertical');value[name].pop('horizontal')
                return value
            def point_checks():
                sid=STAGES[stage_number];projection=panel.original.projection;expected=contract['points'][sid]
                require(projection is not None and projection.mapping_mode=='direct_verified_centers','actual_direct_center_projection_available')
                require(projection.supports_segment_reference is False,'right_original_direct_reference_disables_segments')
                require(tuple(projection.points)==expected,'all_runtime_points_equal_actual_accepted_source_rows')
                rect=panel.original.image_rect();stage=state['stage'];width,height=stage['image']['width'],stage['image']['height']
                require(rect.width()>0 and rect.height()>0,'actual_original_image_rect_available')
                rows=[]
                for row,col,x,y in expected:
                    cell={'row':row,'col':col};require(projection.project(cell)==(x,y),'accepted_logical_cell_maps_exact_source_center')
                    point=panel.original.cell_center(cell);target=(rect.left()+x*rect.width()/width,rect.top()+y*rect.height()/height)
                    require(point is not None and math.isclose(point.x(),target[0],rel_tol=0,abs_tol=1e-7)
                        and math.isclose(point.y(),target[1],rel_tol=0,abs_tol=1e-7),'actual_widget_scales_source_center_at_each_size')
                    require(projection.project({'row':row+.25,'col':col})is None
                        and projection.project({'row':row,'col':col+.25})is None,'fractional_cells_do_not_interpolate')
                    require(projection.cell_at(x,y)is None and panel.original.cell_at(point)is None,'source_and_widget_pixel_inverse_remain_unknown')
                    rows.append({'cell':cell,'source_pixel':[x,y],'widget_pixel':[point.x(),point.y()]})
                require(all(projection.project({'row':value,'col':0})is None for value in (True,float('nan'),float('inf'))),
                    'invalid_and_nonfinite_cells_do_not_map')
                return rows
            def click_left(cell):
                point=panel.grid.cell_center(cell);require(panel.grid.cell_at(point.toPoint())==cell,'real_grid_click_inside_exact_cell')
                previous=len(emissions);QTest.mouseClick(panel.grid,Qt.MouseButton.LeftButton,pos=point.toPoint());gui.processEvents()
                require(len(emissions)==previous+1 and emissions[-1]==cell,'actual_QTest_grid_click_emits_exact_logical_cell')
            def prime():
                for widget in (panel.spawn_detail,panel.enemy_detail):
                    require(widget.document().characterCount()>15,'real_generated_detail_available')
                    cursor=widget.textCursor();cursor.setPosition(1);cursor.setPosition(8,QTextCursor.MoveMode.KeepAnchor);widget.setTextCursor(cursor)
                gui.processEvents();bar=panel.enemy_detail.verticalScrollBar()
                require(bar.maximum()>0,'real_enemy_detail_has_nonzero_scroll_range')
                bar.setValue(max(1,bar.maximum()//2))
                require(bar.value()>0 and bool(panel.spawn_detail.textCursor().selectedText())
                    and bool(panel.enemy_detail.textCursor().selectedText()),'real_nonzero_scroll_and_nonempty_selections')
            def yellow_pixels(image,ratio,point):
                center=(round(point.x()*ratio),round(point.y()*ratio));radius=max(2,math.ceil(5*ratio));values=set()
                for x in range(max(0,center[0]-radius),min(image.width(),center[0]+radius+1)):
                    for y in range(max(0,center[1]-radius),min(image.height(),center[1]+radius+1)):
                        color=image.pixelColor(x,y)
                        if color.red()>=240 and color.green()>=190 and color.blue()<=155:values.add((x,y))
                return values
            def fail(error):
                nonlocal failure,done
                if failure is None:failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
                done=False;window.close();gui.exit(1)
            def later(callback,delay=300):
                def guarded():
                    try:isolated();callback()
                    except BaseException as error:fail(error)
                QTimer.singleShot(delay,guarded)
            def configure():
                nonlocal size_number
                size_number=0;sid=STAGES[stage_number];window.resize(*SIZES[0]);window.show_catalog_battle(sid)
                require(panel.current_stage==window.target_stage.currentData()==sid,'exact_stage_alias_bound_by_actual_MainWindow')
                stage=battle_data()['stages'][sid]
                require(panel.original.image_sha256==stage['image']['sha256'],'actual_bitmap_matches_exact_alias_source')
                state.clear();state['stage']=stage;state['size_observations']=[]
                panel.include_branches.setChecked(False);panel.technical.setChecked(stage_number!=0)
                all_waves=panel.wave_combo.findData(None)
                require(all_waves>=0,'new_stage_all_wave_reference_option_exists')
                panel.wave_combo.setCurrentIndex(all_waves)
                require(panel.enemy_choices.select_branch(OVERVIEW)and panel.enemy_choices.select_value(None),
                    'new_stage_enemy_overview_and_all_enemy_reference_options_exist')
                panel.render_rows()
                require(panel.wave_combo.currentData()is None and panel.enemy_choices.branch.currentData()==OVERVIEW
                    and panel.enemy_combo.currentData()is None and not panel.include_branches.isChecked(),
                    'new_stage_initial_filters_explicitly_reset_to_all_fixed_references')
                expected_ids=[row['id']for wave in stage['waves']for fragment in wave['fragments']
                    for row in fragment['actions']if row['action']['actionType']=='SPAWN']
                require([row['id']for row in panel.rows]==expected_ids,
                    'unfiltered_fixed_SPAWN_rows_match_exact_stage_source_ids')
                known={(r,c)for r,c,*_ in contract['points'][sid]}
                source_rows=deepcopy(panel.rows)
                def eligible(row):
                    # A MOVE may coincide with another source row's START. The
                    # same-widget negative paint fixture retains those markers.
                    moves=[cp for cp in row['route']['checkpoints']if cp['type']=='MOVE'and cp['cell']
                        and(cp['cell']['row'],cp['cell']['col'])in known and cp['cell']!=row['route']['start']]
                    filtered=[other for other in source_rows if other['wave']==row['wave']
                        and other['action']['key']==row['action']['key']]
                    starts={(other['route']['start']['row'],other['route']['start']['col'])
                        for other in filtered if other['route']['start']}
                    return row.get('branch')is None and bool(moves)and bool(known-starts)
                candidates=[row for row in source_rows if eligible(row)]
                require(bool(candidates),'real_main_fixed_SPAWN_row_has_new_accepted_MOVE_checkpoint')
                chosen=candidates[0];wave=panel.wave_combo.findData(chosen['wave'])
                require(wave>=0,'actual_candidate_wave_option_exists');panel.wave_combo.setCurrentIndex(wave)
                enemy_value=next(panel.enemy_combo.itemData(i)for i in range(panel.enemy_combo.count())
                    if panel.enemy_combo.itemData(i)and panel.enemy_combo.itemData(i)[0]==chosen['action']['key'])
                require(panel.enemy_choices.select_value(enemy_value),'actual_manual_enemy_filter_selectable')
                starts={(row['route']['start']['row'],row['route']['start']['col'])for row in panel.rows if row['route']['start']}
                require(bool(known-starts)and any(row['id']==chosen['id']for row in panel.rows),
                    'selected_actual_candidate_filter_leaves_registered_nonspawn_manual_cell')
                state['row_id']=chosen['id'];state['MOVE_cell']=deepcopy(next(cp['cell']for cp in chosen['route']['checkpoints']
                    if cp['type']=='MOVE'and cp['cell']and(cp['cell']['row'],cp['cell']['col'])in known
                    and cp['cell']!=chosen['route']['start']))
                later(exercise)
            def exercise():
                sid=STAGES[stage_number];native();stage=state['stage'];points=point_checks()
                known={(r,c)for r,c,*_ in contract['points'][sid]}
                starts={(row['route']['start']['row'],row['route']['start']['col'])for row in panel.rows if row['route']['start']}
                manual=next(({'row':r,'col':c}for r,c,*_ in contract['points'][sid]if(r,c)not in starts),None)
                unknown=next(({'row':r,'col':c}for r,line in enumerate(stage['map'])for c,index in enumerate(line)
                    if(r,c)not in known and(r,c)not in starts and stage['tiles'][index]['heightType']=='LOWLAND'
                    and stage['tiles'][index]['tileKey']in('tile_floor','tile_road')),None)
                require(manual is not None and unknown is not None,'real_known_and_unknown_ground_cells_available')
                click_left(manual)
                require(panel._tile_cell==panel.grid.reference_cell==panel.original.reference_cell==manual,
                    'manual_known_ground_click_maps_to_matching_original_reference')
                prior=len(inverse_emissions);point=panel.original.cell_center(manual)
                QTest.mouseClick(panel.original,Qt.MouseButton.LeftButton,pos=point.toPoint());gui.processEvents()
                require(len(inverse_emissions)==prior,'real_original_image_click_does_not_invent_inverse_cell')
                click_left(unknown)
                require(panel._tile_cell==panel.grid.reference_cell==unknown and panel.original.reference_cell is None
                    and panel.original.selected is None and panel.original.cell_center(unknown)is None,
                    'unknown_manual_grid_cell_clears_original_marker_and_stays_unmapped')
                require('位置尚未核对'in panel.spawn_detail.toPlainText(),'unknown_cell_has_readable_unmapped_notice')
                panel.spawn_list.setCurrentRow(-1)
                require(panel.spawn_list.currentItem()is None,'list_current_item_explicitly_cleared_before_actual_target_click')
                item=next(panel.spawn_list.item(i)for i in range(panel.spawn_list.count())
                    if panel.spawn_list.item(i).data(Qt.ItemDataRole.UserRole)['id']==state['row_id'])
                panel.spawn_list.scrollToItem(item);gui.processEvents();rect=panel.spawn_list.visualItemRect(item)
                require(rect.isValid()and panel.spawn_list.viewport().rect().contains(rect.center()),'real_SPAWN_list_row_visible_for_QTest')
                QTest.mouseClick(panel.spawn_list.viewport(),Qt.MouseButton.LeftButton,pos=rect.center());gui.processEvents()
                require(panel.original.selected is not None and panel.original.selected['id']==state['row_id']
                    and panel.grid.selected['id']==state['row_id']and panel.original.selected['branch']is None,
                    'actual_list_click_selects_exact_main_fixed_SPAWN_row')
                require(any(point['kind']=='MOVE'and point['row']==state['MOVE_cell']['row']and point['col']==state['MOVE_cell']['col']
                    for point in panel.original.selected['route']['points']),'selected_fixed_route_contains_exact_new_MOVE_cell')
                center=panel.original.cell_center(state['MOVE_cell']);require(center is not None,'selected_MOVE_checkpoint_has_original_map_point')
                selected_object=panel.original.selected;selected_before=deepcopy(selected_object)
                selection_before=selection()
                def geometry():
                    rect=panel.original.image_rect()
                    return {'widget_size':[panel.original.width(),panel.original.height()],
                        'image_rect':[rect.x(),rect.y(),rect.width(),rect.height()],
                        'image_sha256':panel.original.image_sha256,
                        'pixmap_size':[panel.original.pixmap.width(),panel.original.pixmap.height()],
                        'main_client_size':[window.width(),window.height()]}
                geometry_before=geometry()
                # Explicit negative drawing fixture only: keep the exact same
                # QWidget/layout and all controls; do not render_rows or resize.
                try:
                    panel.original.selected=None
                    panel.original.repaint();baseline=panel.original.grab()
                    baseline_geometry=geometry()
                finally:
                    panel.original.selected=selected_object
                    panel.original.repaint()
                after_pixels=panel.original.grab();geometry_after=geometry()
                require(geometry_before==baseline_geometry==geometry_after
                    and baseline.size()==after_pixels.size()
                    and baseline.devicePixelRatio()==after_pixels.devicePixelRatio(),
                    'MOVE_overlay_before_after_has_identical_widget_image_and_layout_geometry')
                require(panel.original.selected is selected_object and panel.original.selected==selected_before
                    and selection()==selection_before,
                    'MOVE_negative_drawing_fixture_restores_exact_selected_object_and_all_selection_state')
                yellow_before=yellow_pixels(baseline.toImage(),baseline.devicePixelRatio(),center)
                yellow_after=yellow_pixels(after_pixels.toImage(),after_pixels.devicePixelRatio(),center)
                added=yellow_after-yellow_before
                require(bool(added),'same_geometry_native_pixels_add_yellow_MOVE_point_beyond_source_background')
                state.update(manual=manual,unknown=unknown,points=points,
                    MOVE_yellow_before=len(yellow_before),MOVE_yellow_after=len(yellow_after),
                    MOVE_added_yellow_pixels=len(added),MOVE_geometry_before=geometry_before,
                    MOVE_geometry_after=geometry_after,MOVE_unchanged_geometry=True)
                later(refresh)
            def refresh():
                prime();state['saved']=selection();panel.render_rows();later(check_refresh)
            def check_refresh():
                nonlocal size_number,stage_number,done
                require(selection()==state['saved'],'same_size_refresh_preserves_options_row_ordinal_reading_selection_and_scroll')
                handle=native();points=point_checks()
                state['size_observations'].append({'requested_size':list(SIZES[size_number]),'native_window':handle,
                    'mapped_accepted_points':points,'same_size_refresh_preserved':True})
                if size_number+1<len(SIZES):
                    state['before_resize']=selection(False);size_number+=1;window.resize(*SIZES[size_number]);later(after_resize)
                    return
                pixels=window.grab();require(not pixels.isNull(),'actual_own_window_pixels_available')
                require(pixels.save(str(images[STAGES[stage_number]]),'PNG'),'actual_stage_PNG_saved')
                observations.append({'stage_id':STAGES[stage_number],'sizes':deepcopy(state['size_observations']),
                    'screenshot':str(images[STAGES[stage_number]]),'screenshot_sha256':sha(images[STAGES[stage_number]]),
                    'native_window':handle,'clicked_registered_ground_cell':state['manual'],
                    'clicked_unknown_ground_cell_left_unmapped':state['unknown'],'actual_selected_main_SPAWN_row_id':state['row_id'],
                    'new_MOVE_cell':state['MOVE_cell'],'MOVE_yellow_before':state['MOVE_yellow_before'],
                    'MOVE_yellow_after':state['MOVE_yellow_after'],'MOVE_added_yellow_pixels':state['MOVE_added_yellow_pixels'],
                    'MOVE_unchanged_geometry':state['MOVE_unchanged_geometry'],
                    'MOVE_geometry_before':state['MOVE_geometry_before'],'MOVE_geometry_after':state['MOVE_geometry_after'],
                    'negative_drawing_fixture':'Only actual MapOriginal.selected temporarily None; same widget/layout, then exact object restored.',
                    'right_original_supports_segments':False,'logical_grid_existing_route_lines_unchanged':True,
                    'actual_enemy_position_or_route_activation':None,'inverse_or_full_calibration_claimed':False})
                stage_number+=1
                if stage_number<len(STAGES):later(configure)
                else:
                    require(len(observations)==len(STAGES),'all_four_actual_stage_images_saved')
                    require(window.run.state==initial_run,'manual_fixed_map_reading_does_not_change_temporary_run_memory')
                    require(bound_files()==before,'selected_public_source_bytes_stable_before_completion');done=True
            def after_resize():
                native();require(selection(False)==state['before_resize'],'resize_preserves_selected_options_row_ordinal_text_and_selections')
                require(all(0<=widget.verticalScrollBar().value()<=widget.verticalScrollBar().maximum()
                    for widget in(panel.spawn_detail,panel.enemy_detail)),'resize_viewports_remain_in_actual_valid_scroll_range')
                point_checks();later(refresh)
            def close_at_deadline():
                nonlocal failure
                if not done and failure is None:failure={'type':'TimeoutError','message':'Four stages/three sizes did not complete before deadline.'}
                window.close()
            later(configure,650);QTimer.singleShot(max(12000,args.visible_ms),close_at_deadline)
            qt_exit=gui.exec();closed=not window.isVisible()
            if qt_exit!=0 or not closed or not done:
                if failure is None:failure={'type':'RuntimeError','message':'Checks/Qt/actual window closure incomplete.'}
            if failure is None:isolated()
            after=bound_files()
            if after!=before and failure is None:failure={'type':'AssertionError','message':'Selected sources changed before actual window closure.'}
    except BaseException as error:
        failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    report={'section':294,'kind':'isolated_native_windows_direct_map_checkpoints','passed':done and failure is None,
        'failure':failure,'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'process_id':os.getpid(),
        'qpa':qpa,'qt_exit_code':qt_exit,'verification_window_closed':closed,'checks':checks,'unique_checks':len(checks),
        'successful_assertion_executions_including_repeated_guards':executions,'stage_observations':observations,
        'expected_stage_ids':list(STAGES),'requested_logical_sizes':[list(size)for size in SIZES],
        'screenshot_count':len(observations),'source_sha256_before':before,'source_sha256_after':after,
        'accepted_point_source':COMPARISON,'actual_accepted_source_points':contract['comparison']['new_accepted_points']if contract else None,
        'prior_direct_points_preserved':contract['prior_direct_points_preserved']if contract else None,
        'regular_image_and_stage_scope_preserved':[contract['regular_images_preserved'],contract['regular_stages_preserved']]if contract else None,
        'remaining_full_map_stage_and_image_gaps':[contract['remaining_full_map_stages'],contract['remaining_full_map_images']]if contract else None,
        'source_guard_is_selected_not_all_transitive_dependencies':True,'temporary_state_root':True,
        'state_paths_replaced_before_constructor':['ROOT','SETTINGS','OPERATOR_STATE','RUN_STATE'],
        'private_state_read_copied_or_restored':False,'external_operation_attempts':attempts,
        'external_entrypoints_blocked_before_original_call':True,'game_operated':False,'game_captures':0,
        'chat_sent':False,'chat_attempted':bool(attempts['desktop_request']or attempts['provider_chat']),
        'original_project_window_operated_or_restarted':False,'owned_supervisor_exit_and_cleanup_required_separately':True,
        'actual_process_termination_verified_by_this_script':False,
        'launch_Popen_PID_must_be_recorded_separately_from_actual_fixture_PID':True,
        'scope':'Four fixed-stage direct-reference UI flows and three sizes each; actual QTest ground cell and main fixed MOVE checkpoint display. Only accepted source centers; no full-plane, inverse, line interpolation, real enemy location, game operation or route recommendation.'}
    with destination.open('x',encoding='utf-8')as stream:stream.write(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return 0 if report['passed']else 1

if __name__=='__main__':raise SystemExit(main())
