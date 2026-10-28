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

