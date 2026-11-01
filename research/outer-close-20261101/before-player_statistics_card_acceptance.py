from pathlib import Path
from unittest.mock import patch
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QLabel

def check(window,gui,require):
    from .player_statistics_acceptance import populate
    from . import player_statistics_card as module
    store,identity=populate(window);window.show_compact();bar=window.compact_window;bar.open_replay();panel=bar.replay_popup.panel;panel.tabs.setCurrentWidget(panel.statistics);page=panel.statistics;controls=page.card_controls;controls.pages.setCurrentIndex(1);gui.processEvents()
    require(not controls.save.isEnabled()and controls.card is None,'statistics_card_not_exported_or_generated_automatically')
    controls.build.click();gui.processEvents();require(controls.card is not None and controls.save.isEnabled(),'explicit_card_build_shows_qualified_local_result')
    text='\n'.join(controls.card.lines);require('不是通关场数'in text and '不是掉落概率'in text and '缺失1局'in text,'card_keeps_denominators_and_missing_evidence')
    require(window.run.state['id']not in text,'card_has_no_private_run_identity')
    old=controls.card;page.refresh();gui.processEvents();require(controls.card is old,'same_statistics_reload_preserves_generated_card')
    controls.fields['parts_count'].setChecked(False);require(controls.card is None and not controls.save.isEnabled(),'changing_fields_invalidates_old_card')
    controls.build.click();require('零件数'not in'\n'.join(controls.card.lines),'only_selected_statistics_fields_rendered')
    target=store.folder/'owned-local-card.png'
    with patch.object(module.QFileDialog,'getSaveFileName',return_value=(str(target),'PNG图片 (*.png)')):require(controls.export(),'manual_card_export_to_owned_temporary_path')
    image=QImage(str(target));card=controls.card
    require(not image.isNull()and image.width()==round(card.width()*card.devicePixelRatioF())and image.height()==round(card.height()*card.devicePixelRatioF()),'exported_file_is_real_readable_png_at_actual_screen_scale')
    require(all(label.geometry().bottom()<card.height()and label.height()>=label.heightForWidth(label.width())for label in card.findChildren(QLabel)),'all_card_explanations_fit_full_exported_image')
    with patch.object(type(store),'records',side_effect=OSError('隔离模拟：历史不可读')):
        page.refresh();require(controls.card is None and page.result is None and not controls.save.isEnabled(),'source_failure_clears_generated_card_and_export')
        require(not controls.generate(),'missing_source_cannot_be_exported_as_zero_sample_card')
    page.refresh();require(controls.card is None,'source_recovery_does_not_reuse_old_card');controls.build.click();gui.processEvents();window.player_validation_target=bar.replay_popup


def check_presentation(window,gui,require):
    from copy import deepcopy
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from .relic_quantities import KETTLE
    before=deepcopy(window.run.state)
    window.show_compact();bar=window.compact_window;bar.open_replay();popup=bar.replay_popup;panel=popup.panel;page=panel.statistics;controls=page.card_controls
    for index in range(25):
        state=deepcopy(before);state.update(id='public-presentation-'+str(index),history=[{'kind':'resource_updated','resource':'gold','value':index,'at':index}],resources={'gold':{'value':index},'parts_count':{'value':index%3}},relics={KETTLE:{'held':True}},tactical_tools={},relic_count=1,inventory_verified=True,config={})
        with patch('rouge.player_history_store.time.time',return_value=1000+index):panel.history_store.archive(state)
    page.refresh();panel.tabs.setCurrentWidget(page);controls.pages.setCurrentIndex(1);page.relic.setCurrentIndex(page.relic.findData(KETTLE));gui.processEvents();global_result=deepcopy(page.result)
    require(page.result['archive_count']==25 and page.result['measures']['gold']['mean']==12,'card447_main_statistics_keeps_all25_real_temporary_archives')
    controls.period.setFocus();QTest.keyClick(controls.period,Qt.Key.Key_Home);QTest.keyClick(controls.period,Qt.Key.Key_Down);gui.processEvents();require(controls.period.currentData()==20,'card447_keyboard_selects_latest20_archives')
    page.scroll.ensureWidgetVisible(controls.build);gui.processEvents();QTest.mouseClick(controls.build,Qt.MouseButton.LeftButton);gui.processEvents();card=controls.card;text='\n'.join(card.lines)
    require('本机归档样本：20局'in text and '平均：14.50'in text,'card447_latest20_scope_uses_archive_order_and_actual_mean')
    require(page.result==global_result and window.run.state==before,'card447_generation_never_changes_main_statistics_or_current_run')
    require('完整清单20局'in text and '归档时持有率：100.0%'in text,'card447_holding_fraction_keeps_qualified_limited_denominator')
    pictures=[v for v in card.findChildren(QLabel)if v.accessibleName().startswith('统计条目图标：')];require(len(pictures)==1 and not pictures[0].pixmap().isNull(),'card447_exact_selected_relic_artwork_is_visible_in_generated_card')
    require(len(card.findChildren(QLabel,'cardMetricValue'))==4,'card447_real_metric_widgets_not_empty_vacuous_geometry_check')
    require(all(v.geometry().bottom()<card.height()and v.height()>=v.heightForWidth(v.width())for v in card.findChildren(QLabel)),'card447_actual_header_metrics_and_limits_fit_export')
    raw=card.png();image=QImage.fromData(raw,'PNG');require(not image.isNull()and image.pixelColor(5,5).name()=='#1e1e20','card447_actual_png_uses_reference_dark_background')
    require(image.width()>image.height(),'card447_export_is_landscape_not_old_vertical_prose_card')
    require(controls.preview.accessibleDescription()==text,'card447_scaled_image_retains_canonical_accessible_text')
    require(all(word in text for word in('不是通关场数','不是掉落概率','版本未完整记录','不会自动上传')),'card447_export_keeps_sample_outcome_probability_and_privacy_limits')
    window.player_card447_images={'dark-card':card.grab(),'preview-wide':popup.grab()};sizes=[]
    page.scroll.ensureWidgetVisible(controls.view);gui.processEvents();QTest.mouseClick(controls.view,Qt.MouseButton.LeftButton);gui.processEvents();viewer=controls.viewer
    require(viewer is not None and viewer.isVisible(),'card447_real_button_opens_independent_large_card_view')
    from PySide6.QtWidgets import QAbstractButton
    close=viewer.findChild(QAbstractButton,'popoverCloseButton');require(close is not None,'card447_actual_close_control_exists')
    from PySide6.QtGui import QColor
    luminance=[]
    for color in(close.getNormalColor(),QColor('#1e1e20')):
        rgb=[v/12.92 if v<=.04045 else((v+.055)/1.055)**2.4 for v in(color.redF(),color.greenF(),color.blueF())]
        luminance.append(sum(a*b for a,b in zip(rgb,(.2126,.7152,.0722))))
    contrast=(max(luminance)+.05)/(min(luminance)+.05)
    require(close.isVisible()and close.width()>=close.fontMetrics().horizontalAdvance('×')and contrast>=4.5 and not close.grab().isNull(),'card447_actual_close_symbol_fits_and_has_high_contrast_on_dark_background')
    controls.open_viewer();gui.processEvents();require(controls.viewer is viewer,'card447_repeated_enlarge_reuses_one_owned_window');window.player_card447_images['enlarged-card']=viewer.grab();QTest.mouseClick(close,Qt.MouseButton.LeftButton);gui.processEvents();require(not viewer.isVisible()and controls.card is card,'card447_actual_mouse_close_keeps_generated_card');controls.open_viewer();gui.processEvents();QTest.keyClick(viewer,Qt.Key.Key_Escape);gui.processEvents()
    require(not viewer.isVisible()and controls.card is card,'card447_actual_escape_closes_viewer_without_destroying_generated_card')
    controls.open_viewer();gui.processEvents();require(controls.viewer is viewer and viewer.isVisible(),'card447_viewer_reopens_same_valid_source')
    from PySide6.QtCore import QRect,QPoint
    binding=bar.game_binding;binding.timer.stop();bar.game_hover.timer.stop()
    snapshot={'key':(123,456),'active':True,'logical_client':QRect(200,150,1000,600),'screen':gui.primaryScreen()}
    binding.apply(snapshot);area=gui.primaryScreen().availableGeometry();viewer.move(area.topLeft()+QPoint(100,100));start=viewer.pos()
    snapshot=dict(snapshot,logical_client=snapshot['logical_client'].translated(19,17));binding.apply(snapshot);gui.processEvents()
    require(viewer in binding.surfaces()and viewer.pos()==start+QPoint(19,17),'card447_enlarged_view_follows_isolated_binding_movement')
    binding.apply(None);gui.processEvents();require(not viewer.isVisible()and not popup.isVisible(),'card447_enlarged_view_hides_with_unavailable_isolated_binding')
    binding.apply(snapshot);gui.processEvents();require(viewer.isVisible()and popup.isVisible(),'card447_enlarged_view_restores_with_same_isolated_binding')
    bar.toggle_visibility();gui.processEvents();require(not viewer.isVisible()and not popup.isVisible(),'card447_visibility_toggle_hides_all_owned_card_windows')
    bar.toggle_visibility();gui.processEvents();require(viewer.isVisible()and popup.isVisible(),'card447_visibility_toggle_restores_card_without_rebuilding')
    binding.enabled=False;binding.ever_bound=False;binding.snapshot=None;binding.previous=None
    for width in(900,550,400):
        popup.resize(width,650);gui.processEvents();sizes.append({'requested_width':width,'actual_width':popup.width(),'actual_height':popup.height(),'preview_width':controls.preview.width()})
        require(controls.scroll.horizontalScrollBar().maximum()==0,'card447_preview_has_no_horizontal_scroll_at_actual_width_'+str(width))
        require(controls.preview.pixmap().deviceIndependentSize().width()<=controls.preview.contentsRect().width()+.5/controls.preview.devicePixelRatioF() and controls.preview.pixmap().devicePixelRatioF()==controls.preview.devicePixelRatioF(),'card447_preview_fits_current_viewport_at_actual_pixel_ratio_'+str(width))
        require(controls.card is card and card.png()==raw,'card447_resize_keeps_full_export_and_exact_card_'+str(width))
    window.player_card447_sizes=sizes;window.player_card447_images['preview-narrow']=popup.grab()
    page.refresh();gui.processEvents();require(controls.card is card and controls.period.currentData()==20,'card447_same_reload_keeps_generated_limited_card_and_selection')
    target=panel.history_store.folder/'public-card447-export.png'
    from . import player_statistics_card as module
    with patch.object(module.QFileDialog,'getSaveFileName',return_value=(str(target),'PNG图片 (*.png)')):require(controls.export(),'card447_existing_manual_export_writes_only_owned_temporary_file')
    exported=QImage(str(target));require(not exported.isNull()and exported.size()==image.size()and target.read_bytes()==raw,'card447_export_keeps_full_original_pixels_after_preview_resize')
    controls.period.setCurrentIndex(0);require(not viewer.isVisible(),'card447_range_change_closes_owned_stale_enlarged_view');gui.processEvents();require(controls.card is None and controls.preview.original.isNull()and not controls.save.isEnabled(),'card447_range_change_clears_stale_picture_and_export')
    QTest.mouseClick(controls.build,Qt.MouseButton.LeftButton);gui.processEvents();require('本机归档样本：25局'in'\n'.join(controls.card.lines),'card447_all_archives_can_be_generated_after_limited_scope')
    with patch.object(page.store,'records',side_effect=OSError('isolated unavailable card archive')):page.refresh()
    require(page.result is None and controls.card is None and controls.preview.original.isNull()and not controls.save.isEnabled(),'card447_source_loss_clears_old_values_picture_and_export')
    require(not controls.generate(),'card447_unknown_source_not_rendered_as_zero_sample_card');page.refresh();require(controls.card is None,'card447_source_recovery_does_not_automatically_reuse_old_card')
    page.scroll.ensureWidgetVisible(controls.build);gui.processEvents();QTest.mouseClick(controls.build,Qt.MouseButton.LeftButton);gui.processEvents();require(controls.card is not None,'card447_explicit_build_after_recovery_works')
    require(window.run.state==before,'card447_entire_read_export_workflow_never_changes_current_run');window.player_card447_images['preview-final']=popup.grab();window.player_validation_target=popup

