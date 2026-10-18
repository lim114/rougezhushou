"""Root-promoted actual Windows fixture for fixed direct ground centers.
Cache preparation must not execute this file. Sparse points are not a whole map.
"""
import argparse
from contextlib import ExitStack
from copy import deepcopy
from datetime import datetime,timezone
import hashlib,json,math,os
from pathlib import Path,PurePosixPath
import sys,tempfile,traceback
from unittest.mock import patch
ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())
sys.path.insert(0,str(ROOT))
CANONICAL='scripts/verify_direct_map_window_308.py'
PACKET='research/p3-map-direct-ground-308'
MANIFEST=PACKET+'/source-manifest.json'
COMPARISON=PACKET+'/build-receipt.json'
DATA='rouge/data/fixed-landmark-references.json'
ROOT_COMPARISON='verification/sections/308-preparation/first-frozen-comparison.json'
ROOT_COMPARISON_SHA256='a0141c9bb9fb6c405e23157c62a09eb31861855022e803004bec9d50c85df0f4'
MANIFEST_SHA256='a47baddc0d8201afd63b415602f7ebf572d70efcc09fd6d9e4c0875fbba2ddff'
COMPARISON_SHA256='5aab9ac1d1c96f2d602c1ebb0d2dfeda534e14f61689ddd8b5b7b201d655bbf7'  # Bind only after the root's actual source build.
DATA_SHA256='7e8044bcbdb5cf9605152f55fa2d262336e19bbf5fc74f8a8b9352f2a6fc1dde'  # Bind only to the exact promoted append, never prior107.
STAGES=('ro6_n_5_1','ro6_e_5_1','ro6_n_5_5','ro6_e_5_5')
SIZES=((1280,850),(1440,900),(1520,940))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_bytes())
def public_path(name):
    if type(name)is not str:raise ValueError('Exact public relative path required.')
    pure=PurePosixPath(name)
    if pure.is_absolute()or'..'in pure.parts or'\\'in name or':'in name:raise ValueError('Source path outside public root.')
    p=ROOT.joinpath(*pure.parts)
    if not p.is_file()or p.is_symlink()or not p.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Regular public source required: '+name)
    return p
def grid_digest(stage):
    raw=[[{k:stage['tiles'][index].get(k)for k in('tileKey','heightType','buildableType','passableMask')}for index in row]for row in stage['map']]
    return hashlib.sha256(json.dumps(raw,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def source_contract():
    if any(type(pin)is not str or len(pin)!=64 for pin in(MANIFEST_SHA256,COMPARISON_SHA256,DATA_SHA256)):
        raise RuntimeError('Root actual build and exact promoted DATA/build-receipt pins are not yet bound; no Qt may start.')
    for name,pin in((MANIFEST,MANIFEST_SHA256),(COMPARISON,COMPARISON_SHA256),(DATA,DATA_SHA256),(ROOT_COMPARISON,ROOT_COMPARISON_SHA256)):
        if sha(public_path(name))!=pin:raise ValueError('Reviewed source bytes changed: '+name)
    manifest=read(ROOT/MANIFEST)
    if manifest['section']!=308 or manifest['all_source_eligible_requests']!=67 or manifest['agreement_tolerance_px']!=4:
        raise ValueError('The complete67 source/unchanged4px contract changed.')
    for name,pin in manifest['files'].items():
        path=public_path(name)
        if sha(path)!=pin['sha256']or path.stat().st_size!=pin['bytes']:raise ValueError('Frozen original source changed: '+name)
    comparison=read(ROOT/COMPARISON);runtime=read(ROOT/DATA);folder=ROOT/PACKET
    source=read(folder/'source-records.json');request=read(folder/'REQUEST_MANIFEST.json')
    originals={label:read(folder/('READER_'+label+'_ORIGINAL.json'))for label in('A','B')}
    rows=comparison['new_agreement_comparisons']
    request_rows={r['request_id']:r for group in request['groups']for r in group['all_requests']}
    if len(rows)!=67 or len(request_rows)!=67 or len({r['request_id']for r in rows})!=67 or comparison['new_requested_points']!=len(rows):
        raise ValueError('Source request/comparison was omitted or duplicated.')
    if set(request_rows)!={r['request_id']for r in rows}:raise ValueError('Comparison differs from all original requests.')
    root_rows={r['request_id']:r for r in read(ROOT/ROOT_COMPARISON)['comparisons']}
    if set(root_rows)!=set(request_rows):raise ValueError('Root independent first comparison has another source domain.')
    accepted=[];rejected=[]
    for row in rows:
        requested=request_rows[row['request_id']]
        if(row['row'],row['col'],row['tile_key'])!=(requested['row'],requested['col'],requested['tile_key']):
            raise ValueError('Comparison refers to another logical source cell.')
        pixels={}
        for label,key,pixel_field in(('A','observed_pixel','observed_pixel'),('B','independent_pixel','pixel')):
            pointer=row['original_reader_rows'][label]
            if pointer['file']!='READER_'+label+'_ORIGINAL.json'or pointer['pixel_field']!=pixel_field:raise ValueError('Reader pointer identity changed.')
            image=originals[label]['images'][pointer['image_index']];original=image['readings'][pointer['reading_index']]
            if image['stage_id']!=row['reference']or any(original[k]!=row[k]for k in('row','col','tile_key','request_id')):
                raise ValueError('Comparison lost original reader row identity.')
            if original[pixel_field]!=row[key]or original['reason']!=row['reader_reason'][label]:raise ValueError('Original pixels or reason were rewritten.')
            pixels[label]=original[pixel_field]
        one,two=pixels['A'],pixels['B'];distance=math.dist(one,two)if one is not None and two is not None else None
        admitted=distance is not None and distance<=4
        if row['agreement_px']!=distance or row['accepted_for_runtime']is not admitted:raise ValueError('Exact unrounded4px acceptance changed.')
        original_root=root_rows[row['request_id']]
        if original_root['original_A']!=one or original_root['original_B']!=two or original_root['unrounded_distance']!=distance or original_root['accepted']is not admitted:
            raise ValueError('Builder differs from the independent first frozen root comparison.')
        (accepted if admitted else rejected).append(row)
    if(comparison['new_accepted_points'],comparison['new_rejected_or_unknown_points'])!=(len(accepted),len(rejected)):
        raise ValueError('Comparison totals differ from its actual rows.')
    stages=read(ROOT/'rouge/data/battle-previews.json')['stages'];points={};rejected_by_stage={}
    for sid in STAGES:
        stage=stages[sid];binding=runtime['stages'][sid];reference=binding['reference'];record=runtime['references'][reference]
        identity=source['stages'][sid]
        if binding['image_file']!=stage['image']['file']or binding['level_sha256']!=stage['level_source']['sha256']:
            raise ValueError('An explicit alias borrowed another filename or level.')
        if identity['image']!=stage['image']or identity['level_source']!=stage['level_source']or grid_digest(stage)!=identity['grid_sha256']:
            raise ValueError('Alias original image/level/grid changed.')
        bitmap=public_path('rouge/data/'+stage['image']['file'])
        if sha(bitmap)!=stage['image']['sha256']or bitmap.stat().st_size!=stage['image']['bytes']:raise ValueError('Actual bitmap changed.')
        if record['bitmap_sha256']!=stage['image']['sha256']or record['grid_sha256']!=grid_digest(stage):raise ValueError('Direct record no longer matches source image/grid.')
        selected=[r for r in accepted if r['reference']==reference]
        expected=tuple((r['row'],r['col'],*r['observed_pixel'])for r in selected)
        actual=tuple((r['row'],r['col'],*r['observed_pixel'])for r in record['points'])
        if not expected or actual!=expected:raise ValueError('Runtime points differ from every accepted first original observation: '+sid)
        for point,original in zip(record['points'],selected):
            if any(point[key]!=original[key]for key in('tile_key','independent_pixel','agreement_px','original_reader_rows')):
                raise ValueError('Runtime source/peer identity differs from original comparison.')
        points[sid]=expected;rejected_by_stage[sid]=[r for r in rejected if r['reference']==reference]
    prior=read(folder/'prior-direct-references.json')
    if sha(folder/'prior-direct-references.json')!='dc43bbbe70eab6f11cc8661c3bfeab994000ea614ea0f8c999a596f5cb2c445a':raise ValueError('Prior107 byte authority changed.')
    if any(runtime[group].get(key)!=value for group in('references','stages')for key,value in prior[group].items()):raise ValueError('An old107 exact record changed.')
    regular=read(ROOT/'rouge/data/battle-map-projections.json')
    if(ROOT/'rouge/data/battle-map-projections.json').read_bytes()!=(folder/'prior-regular-projections.json').read_bytes()or(len(regular['calibrations']),len(regular['stages']))!=(12,24):
        raise ValueError('The original12/24 regular bytes changed.')
    unbound={sid:s for sid,s in stages.items()if sid not in regular['stages']}
    if(len(unbound),len({s['image']['sha256']for s in unbound.values()}))!=(81,59):raise ValueError('Sparse points were promoted into whole-map scope.')
    return{'comparison':comparison,'runtime':runtime,'points':points,'rejected':rejected_by_stage,'prior_direct_points_preserved':107,
        'total_partial_scope':[len(runtime['references']),len(runtime['stages']),sum(len(r['points'])for r in runtime['references'].values())],
        'regular_images_preserved':12,'regular_stages_preserved':24,'remaining_full_map_stages':81,'remaining_full_map_images':59}

def bound_files():
    names={CANONICAL,MANIFEST,COMPARISON,DATA,ROOT_COMPARISON,'rouge/app.py','rouge/battle_preview.py','rouge/battle_view.py',
        'rouge/map_projection.py','rouge/fixed_landmark_mapping.py','rouge/player_tile_information.py','rouge/branch_choice.py',
        'rouge/branch_reference_view.py','rouge/spawn_reference.py','rouge/ui_state.py','rouge/data/battle-previews.json',
        'rouge/data/battle-map-projections.json','scripts/extend_direct_landmark_308.py','tests/test_direct_landmark_308.py',
        'tests/test_direct_landmark_303.py','tests/test_direct_landmark_294.py','tests/test_direct_landmark_288.py'}
    names.update(read(ROOT/MANIFEST)['files'])
    names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/PACKET).rglob('*')if p.is_file())
    stages=read(ROOT/'rouge/data/battle-previews.json')['stages']
    names.update('rouge/data/'+stages[sid]['image']['file']for sid in STAGES)
    return{name:sha(public_path(name))for name in sorted(names)}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt',required=True);parser.add_argument('--visible-ms',type=int,default=120000)
    args=parser.parse_args();destination=Path(args.receipt).resolve()
    if destination.exists():raise FileExistsError('Preserve the first actual receipt.')
    if args.visible_ms<=0:raise ValueError('Positive --visible-ms required.')
    destination.parent.mkdir(parents=True,exist_ok=True)
    images={sid:destination.with_name(destination.stem+'-'+sid+'.png')for sid in STAGES}
    extra_images=[]
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
        with tempfile.TemporaryDirectory(prefix='rouge-308-direct-map-')as folder,ExitStack()as stack:
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
            window=PublicWindow();stack.callback(gui.processEvents);stack.callback(window.close)
            window.setWindowTitle('第308节 · 一步之遥与彼处水如酒已核地格（公开隔离验收）')
            window.resize(*SIZES[0]);window.show()
            panel=window.battle_preview;tabs=window.centralWidget();initial_run=deepcopy(window.run.state)
            calculation_before=tuple((window.relic_list.item(i).data(Qt.ItemDataRole.UserRole),window.relic_list.item(i).checkState().value)for i in range(window.relic_list.count()))
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
                known={(r,c)for r,c,*_ in expected}
                rejected=contract['rejected'][sid]
                require(all(projection.project({'row':r['row'],'col':r['col']})is None for r in rejected),
                    'every_rejected_or_unreadable_original_source_cell_remains_unmapped')
                require(all(projection.project({'row':r,'col':c})is None
                    for r,line in enumerate(stage['map'])for c,_ in enumerate(line)if(r,c)not in known),
                    'every_unlisted_cell_including_unsupported_raised_surfaces_remains_unmapped')
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
            def highlight_pixels(image,ratio,point):
                center=(round(point.x()*ratio),round(point.y()*ratio));radius=max(6,math.ceil(17*ratio));values=set()
                for x in range(max(0,center[0]-radius),min(image.width(),center[0]+radius+1)):
                    for y in range(max(0,center[1]-radius),min(image.height(),center[1]+radius+1)):
                        color=image.pixelColor(x,y);r,g,b=color.red(),color.green(),color.blue()
                        if(r>=210 and 100<=g<=205 and b>=210)or(r>=240 and g>=190 and b<=155)or min(r,g,b)>=235:
                            values.add((x,y))
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
            def choose_row(row_id):
                item=next(panel.spawn_list.item(i)for i in range(panel.spawn_list.count())
                    if panel.spawn_list.item(i).data(Qt.ItemDataRole.UserRole)['id']==row_id)
                panel.spawn_list.setCurrentRow(-1);panel.spawn_list.scrollToItem(item);gui.processEvents()
                rect=panel.spawn_list.visualItemRect(item)
                require(rect.isValid()and panel.spawn_list.viewport().rect().contains(rect.center()),'actual_fixed_source_row_visible_for_QTest')
                QTest.mouseClick(panel.spawn_list.viewport(),Qt.MouseButton.LeftButton,pos=rect.center());gui.processEvents()
                require(panel.original.selected is not None and panel.original.selected['id']==row_id,'actual_QTest_fixed_source_row_selected')
            def configure():
                nonlocal size_number
                size_number=0;sid=STAGES[stage_number];window.resize(*SIZES[0]);window.show_catalog_battle(sid)
                require(panel.current_stage==window.target_stage.currentData()==sid,'exact_stage_alias_bound_by_actual_MainWindow')
                stage=battle_data()['stages'][sid]
                require(panel.original.image_sha256==stage['image']['sha256'],'actual_bitmap_matches_exact_alias_source')
                state.clear();state['stage']=stage;state['size_observations']=[]
                panel.include_branches.setChecked(False);panel.technical.setChecked(False)
                all_waves=panel.wave_combo.findData(None)
                require(all_waves>=0,'new_stage_all_wave_reference_option_exists');panel.wave_combo.setCurrentIndex(all_waves)
                require(panel.enemy_choices.select_branch(OVERVIEW)and panel.enemy_choices.select_value(None),
                    'new_stage_enemy_overview_and_all_enemy_reference_options_exist')
                panel.render_rows()
                expected_ids=[row['id']for wave in stage['waves']for fragment in wave['fragments']
                    for row in fragment['actions']if row['action']['actionType']=='SPAWN']
                require([row['id']for row in panel.rows]==expected_ids,'unfiltered_fixed_SPAWN_rows_match_exact_stage_source_ids')
                require(bool(panel.rows),'actual_source_has_readable_fixed_enemy_row')
                chosen=deepcopy(panel.rows[0]);state['row_id']=chosen['id']
                wave=panel.wave_combo.findData(chosen['wave']);require(wave>=0,'actual_reading_wave_option_exists');panel.wave_combo.setCurrentIndex(wave)
                enemy_value=next(panel.enemy_combo.itemData(i)for i in range(panel.enemy_combo.count())
                    if panel.enemy_combo.itemData(i)and panel.enemy_combo.itemData(i)[0]==chosen['action']['key'])
                require(panel.enemy_choices.select_value(enemy_value),'actual_manual_enemy_filter_selectable')
                choose_row(chosen['id'])
                # Branch scope is an actual UI filter change, not an assumed
                # activation or an invented route. Accepted map identity is fixed.
                baseline=tuple(panel.original.projection.points)
                scope=[]
                for include in(True,False):
                    panel.include_branches.setChecked(include);gui.processEvents()
                    require(panel.current_stage==sid and tuple(panel.original.projection.points)==baseline,
                        'same_map_branch_scope_does_not_change_verified_source_centers')
                    scope.append({'include_branches':include,'actual_filtered_rows':len(panel.rows),
                        'conditional_reference_rows':sum(bool(row.get('branch'))for row in panel.rows),
                        'stage_id':panel.current_stage})
                state['branch_scope_observations']=scope
                later(exercise)
            def assert_click_mapping(cell):
                matching=[row for row in panel.rows if row['route']['start']==cell]
                click_left(cell)
                if matching:
                    require(panel.original.selected is not None and panel.grid.selected is not None
                        and panel.original.selected['id']==matching[0]['id']and panel.original.selected['route']['start']==cell,
                        'accepted_START_cell_click_reads_exact_existing_source_row_without_fabricated_tile_state')
                    return 'existing_source_row_start'
                require(panel._tile_cell==panel.grid.reference_cell==panel.original.reference_cell==cell
                    and panel.original.selected is None,'accepted_ground_click_maps_matching_original_manual_reference')
                return 'manual_ground_reference'
            def click_unknown():
                sid=STAGES[stage_number];starts={tuple(row['route']['start'][k]for k in('row','col'))
                    for row in panel.rows if row['route']['start']}
                rejected=contract['rejected'][sid]
                candidate=next((r for r in rejected if(r['row'],r['col'])not in starts),rejected[0]if rejected else None)
                if candidate is None:
                    known={(r,c)for r,c,*_ in contract['points'][sid]}
                    candidate=next({'row':r,'col':c,'request_id':None,'rejection':'unlisted_source_cell'}
                        for r,line in enumerate(state['stage']['map'])for c,_ in enumerate(line)if(r,c)not in known)
                cell={'row':candidate['row'],'col':candidate['col']};click_left(cell)
                require(panel.original.cell_center(cell)is None and panel.original.reference_cell is None
                    and(cell['row'],cell['col'])not in panel.original.marker_cells(),
                    'actual_unknown_grid_click_does_not_acquire_an_original_source_marker')
                if(cell['row'],cell['col'])not in starts:
                    require(panel._tile_cell==panel.grid.reference_cell==cell and panel.original.selected is None,
                        'unknown_manual_tile_retains_logical_reading_and_clears_old_original_selection')
                    require('位置尚未核对'in panel.spawn_detail.toPlainText(),'unknown_cell_has_readable_unmapped_notice')
                return cell,deepcopy(candidate)
            def selection_paint_proof(cell):
                center=panel.original.cell_center(cell);require(center is not None,'manual_source_selection_has_actual_scaled_center')
                original_selected=panel.original.selected;selected_value=deepcopy(original_selected)
                original_reference=panel.original.reference_cell;reference_value=deepcopy(original_reference)
                saved=selection()
                def geometry():
                    rect=panel.original.image_rect()
                    return{'widget_size':[panel.original.width(),panel.original.height()],
                        'image_rect':[rect.x(),rect.y(),rect.width(),rect.height()],
                        'image_sha256':panel.original.image_sha256,'pixmap_size':[panel.original.pixmap.width(),panel.original.pixmap.height()],
                        'main_client_size':[window.width(),window.height()]}
                before_geometry=geometry()
                try:
                    panel.original.selected=None;panel.original.reference_cell=None;panel.original.repaint()
                    baseline=panel.original.grab();baseline_geometry=geometry()
                finally:
                    panel.original.selected=original_selected;panel.original.reference_cell=original_reference;panel.original.repaint()
                after_pixels=panel.original.grab();after_geometry=geometry()
                require(before_geometry==baseline_geometry==after_geometry and baseline.size()==after_pixels.size()
                    and baseline.devicePixelRatio()==after_pixels.devicePixelRatio(),'selection_overlay_uses_identical_widget_image_and_layout_geometry')
                require(panel.original.selected is original_selected and panel.original.selected==selected_value
                    and panel.original.reference_cell is original_reference and panel.original.reference_cell==reference_value
                    and selection()==saved,'negative_paint_fixture_restores_exact_selected_objects_and_all_control_state')
                before_pixels=highlight_pixels(baseline.toImage(),baseline.devicePixelRatio(),center)
                painted_pixels=highlight_pixels(after_pixels.toImage(),after_pixels.devicePixelRatio(),center)
                added=painted_pixels-before_pixels
                require(bool(added),'same_geometry_native_selection_adds_highlight_pixels_beyond_original_background')
                return{'cell':deepcopy(cell),'highlight_before':len(before_pixels),'highlight_after':len(painted_pixels),
                    'added_highlight_pixels':len(added),'geometry_before':before_geometry,'geometry_after':after_geometry,
                    'unchanged_geometry':True,'exact_selected_objects_restored':True,
                    'fixture':'Only original.selected and reference_cell temporarily None on the same QWidget; exact objects restored; no render_rows/resize.'}
            def exercise():
                sid=STAGES[stage_number];native();points=point_checks();clicked=[]
                for point in points:
                    cell=point['cell'];mode=assert_click_mapping(cell)
                    require(panel.original.cell_center(cell)is not None,'every_accepted_actual_grid_click_has_its_verified_source_center')
                    clicked.append({**point,'actual_grid_click':True,'reading_mode':mode})
                require(len(clicked)==len(contract['points'][sid]),'all_actual_accepted_alias_points_clicked_not_just_one_example')
                first=points[0]['cell'];assert_click_mapping(first);prior=len(inverse_emissions);saved=selection()
                QTest.mouseClick(panel.original,Qt.MouseButton.LeftButton,pos=panel.original.cell_center(first).toPoint());gui.processEvents()
                require(len(inverse_emissions)==prior and selection()==saved,'actual_original_image_click_never_invents_inverse_cell_or_changes_reading')
                unknown,rejected=click_unknown()
                # Read a real fixed row for genuine long enemy text, then leave a
                # verified manual cell selected if available. No padding is used.
                choose_row(state['row_id'])
                starts={(row['route']['start']['row'],row['route']['start']['col'])for row in panel.rows if row['route']['start']}
                manual=next((p['cell']for p in points if(p['cell']['row'],p['cell']['col'])not in starts),first)
                selected_mode=assert_click_mapping(manual);paint=selection_paint_proof(manual)
                supported_moves=[{'row_id':row['id'],'cell':deepcopy(cp['cell'])}for row in panel.rows
                    for cp in row['route']['checkpoints']if cp['type']=='MOVE'and cp['cell']
                    and panel.original.cell_center(cp['cell'])is not None]
                state.update(manual=manual,unknown=unknown,rejected_source=rejected,points=points,
                    clicked_accepted_points=clicked,selection_paint=paint,selected_mode=selected_mode,
                    supported_MOVE_source_rows=supported_moves)
                later(refresh)
            def refresh():
                prime();state['saved']=selection();panel.render_rows();later(check_refresh)
            def check_refresh():
                nonlocal size_number,stage_number,done
                require(selection()==state['saved'],'same_size_refresh_preserves_options_row_ordinal_reading_selection_and_scroll')
                handle=native();points=point_checks()
                state['size_observations'].append({'requested_size':list(SIZES[size_number]),'native_window':handle,
                    'mapped_accepted_points':points,'actually_clicked_accepted_points':deepcopy(state['clicked_accepted_points']),
                    'clicked_unknown_cell_left_unmapped':deepcopy(state['unknown']),
                    'selection_paint':deepcopy(state['selection_paint']),'same_size_refresh_preserved':True})
                if size_number+1<len(SIZES):
                    state['before_resize']=selection(False);size_number+=1;window.resize(*SIZES[size_number]);later(after_resize)
                    return
                pixels=window.grab();require(not pixels.isNull(),'actual_own_window_pixels_available')
                require(pixels.save(str(images[STAGES[stage_number]]),'PNG'),'actual_stage_PNG_saved')
                observations.append({'stage_id':STAGES[stage_number],'sizes':deepcopy(state['size_observations']),
                    'screenshot':str(images[STAGES[stage_number]]),'screenshot_sha256':sha(images[STAGES[stage_number]]),
                    'native_window':handle,'clicked_registered_ground_cell':state['manual'],
                    'clicked_unknown_ground_cell_left_unmapped':state['unknown'],'actual_reading_fixed_SPAWN_row_id':state['row_id'],
                    'rejected_source_row':state['rejected_source'],'branch_scope_observations':state['branch_scope_observations'],
                    'supported_MOVE_source_rows':state['supported_MOVE_source_rows'],
                    'MOVE_is_not_a_required_or_presumed_feature':True,
                    'selection_paint':deepcopy(state['selection_paint']),
                    'right_original_supports_segments':False,'logical_grid_existing_route_lines_unchanged':True,
                    'actual_enemy_position_or_route_activation':None,'inverse_or_full_calibration_claimed':False})
                if stage_number==0:
                    unknown,rejected=click_unknown();gui.processEvents()
                    require(panel.original.cell_center(unknown)is None and not panel.technical.isChecked(),
                        'representative_unknown_surface_is_actually_unmapped_in_player_mode')
                    cursor=panel.spawn_detail.document().find('位置尚未核对')
                    if not cursor.isNull():panel.spawn_detail.setTextCursor(cursor);panel.spawn_detail.ensureCursorVisible();gui.processEvents()
                    rejected_path=destination.with_name(destination.stem+'-unmapped-'+STAGES[stage_number]+'.png')
                    if rejected_path.exists():raise FileExistsError('Preserve first actual unknown-surface PNG.')
                    pixels=window.grab();require(not pixels.isNull()and pixels.save(str(rejected_path),'PNG'),'actual_unknown_surface_player_PNG_saved')
                    extra_images.append({'name':STAGES[stage_number]+'-unknown','path':str(rejected_path),
                        'sha256':sha(rejected_path),'native_window':native(),'player_text':True,
                        'source_request_id':rejected['request_id'],'source_rejection':rejected['rejection'],'original_point_for_cell':None})
                stage_number+=1
                if stage_number<len(STAGES):later(configure)
                else:
                    require(len(observations)==len(STAGES),'all_four_actual_stage_alias_images_saved')
                    require(window.run.state==initial_run,'manual_fixed_map_reading_does_not_change_temporary_run_memory')
                    calculation_after=tuple((window.relic_list.item(i).data(Qt.ItemDataRole.UserRole),window.relic_list.item(i).checkState().value)for i in range(window.relic_list.count()))
                    require(calculation_after==calculation_before,'map_reading_does_not_change_calculation_relic_checkboxes')
                    require(len(extra_images)==1,'actual_unknown_surface_player_image_saved')
                    require(bound_files()==before,'selected_public_source_bytes_stable_before_completion');done=True
            def after_resize():
                native();require(selection(False)==state['before_resize'],'resize_preserves_selected_options_row_ordinal_text_and_selections')
                require(all(0<=widget.verticalScrollBar().value()<=widget.verticalScrollBar().maximum()
                    for widget in(panel.spawn_detail,panel.enemy_detail)),'resize_viewports_remain_in_actual_valid_scroll_range')
                point_checks();later(exercise)
            def close_at_deadline():
                nonlocal failure
                if not done and failure is None:failure={'type':'TimeoutError','message':'Four stage aliases/three sizes did not complete before deadline.'}
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
    report={'section':308,'kind':'isolated_native_windows_direct_ground_centers','passed':done and failure is None,
        'failure':failure,'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'process_id':os.getpid(),
        'qpa':qpa,'qt_exit_code':qt_exit,'verification_window_closed':closed,'checks':checks,'unique_checks':len(checks),
        'successful_assertion_executions_including_repeated_guards':executions,'stage_observations':observations,
        'expected_stage_ids':list(STAGES),'requested_logical_sizes':[list(size)for size in SIZES],
        'screenshots':[{"name":row['stage_id']+'-mapped',"path":row['screenshot'],"sha256":row['screenshot_sha256'],"native_window":row['native_window'],"player_text":True}for row in observations]+extra_images,
        'extra_screenshots':extra_images,'screenshot_count':len(observations)+len(extra_images),'source_sha256_before':before,'source_sha256_after':after,
        'accepted_point_source':COMPARISON,'actual_accepted_source_points':contract['comparison']['new_accepted_points']if contract else None,
        'prior_direct_points_preserved':contract['prior_direct_points_preserved']if contract else None,
        'source_requested_points':contract['comparison']['new_requested_points']if contract else None,
        'rejected_or_unknown_source_points':contract['comparison']['new_rejected_or_unknown_points']if contract else None,
        'total_partial_scope_from_current_data':contract['total_partial_scope']if contract else None,
        'alias_point_readings_are_not_added_to_distinct_source_acceptance':True,
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
        'scope':'Four exact aliases and three actual sizes each; every accepted source cell clicked through the logical grid. Manual selection highlight uses same-geometry source-background difference. MOVE observations are conditional, never required or fabricated. Unknown cells remain unmapped; no inverse, original-map segments, whole-plane, live enemy location, game operation or route recommendation.'}
    with destination.open('x',encoding='utf-8')as stream:stream.write(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return 0 if report['passed']else 1

if __name__=='__main__':raise SystemExit(main())
