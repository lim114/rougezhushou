"""Derive a second independent temp/offscreen probe without changing original evidence."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
text = (HERE / 'diagnose_tab_minimums.py').read_text(encoding='utf-8')
text = text.replace("output = HERE / 'OFFSCREEN_TAB_MINIMUMS.json'", "output = HERE / 'OFFSCREEN_CAPTURE_SCROLL_CANDIDATE.json'", 1)
text = text.replace('from PySide6.QtWidgets import QApplication, QLabel, QWidget',
                    'from PySide6.QtWidgets import QApplication, QLabel, QWidget, QScrollArea', 1)
start = text.index('            removals = []\n')
end = text.index("            record['one_page_removal_diagnostics_restored_each_time'] = removals\n", start)
end += len("            record['one_page_removal_diagnostics_restored_each_time'] = removals\n")
replacement = '''            # This is a temporary widget-only candidate, never a production patch.
            capture_page, capture_title, capture_icon = page_list[0]
            index = tabs.indexOf(capture_page)
            kept_fields = {name: id(getattr(window, name)) for name in
                ('connect_button', 'sample_button', 'auto', 'preview', 'observed_text',
                 'run_summary', 'reset_run_button', 'capture_operator_picture', 'operator_summary')}
            tabs.removeTab(index)
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(capture_page)
            tabs.insertTab(index, scroll, capture_icon, capture_title)
            tabs.setCurrentWidget(panel); flush(); window.resize(1050, 720); flush()
            candidate = {'kind': 'IN_MEMORY_CAPTURE_PAGE_SCROLL_WRAPPER_ONLY_NOT_LIVE_PATCH',
                'window': widget_stats(window), 'tabs': widget_stats(tabs), 'requested': [1050, 720],
                'actual': size(window.size()), 'reading_size': size(panel.player_detail.size()),
                'scroll_widget': widget_stats(scroll), 'capture_content': widget_stats(capture_page),
                'all_recorded_widget_field_identities_preserved': all(id(getattr(window, name)) == identity
                    for name, identity in kept_fields.items()),
                'preview_minimum_height_unchanged': window.preview.minimumHeight()}
            assert size(window.size()) == [1050, 720]
            assert window.minimumSizeHint().height() < 720
            assert candidate['all_recorded_widget_field_identities_preserved']
            assert window.preview.minimumHeight() == 180
            tabs.setCurrentWidget(scroll); flush()
            assert scroll.verticalScrollBar().maximum() > 0
            footer = capture_page.layout().itemAt(capture_page.layout().count() - 1).widget()
            scroll.ensureWidgetVisible(footer, 0, 0); flush()
            candidate['footer_scroll_value'] = scroll.verticalScrollBar().value()
            candidate['vertical_scroll_maximum'] = scroll.verticalScrollBar().maximum()
            candidate['footer_visible_region_nonempty'] = not footer.visibleRegion().isEmpty()
            assert candidate['footer_scroll_value'] > 0 and candidate['footer_visible_region_nonempty']
            scroll.ensureWidgetVisible(window.connect_button, 0, 0); flush()
            candidate['top_scroll_value'] = scroll.verticalScrollBar().value()
            candidate['connect_button_visible_region_nonempty'] = not window.connect_button.visibleRegion().isEmpty()
            assert candidate['connect_button_visible_region_nonempty']
            record['in_memory_candidate'] = candidate
'''
text = text[:start] + replacement + text[end:]
with (HERE / 'diagnose_capture_scroll_candidate.py').open('x', encoding='utf-8') as stream:
    stream.write(text)
runner = (HERE / 'run_first_offscreen_diagnostic.py').read_text(encoding='utf-8')
runner = runner.replace("source = here / 'diagnose_tab_minimums.py'", "source = here / 'diagnose_capture_scroll_candidate.py'", 1)
runner = runner.replace("('first-offscreen' + suffix)", "('scroll-candidate-first-offscreen' + suffix)", 1)
with (HERE / 'run_scroll_candidate.py').open('x', encoding='utf-8') as stream:
    stream.write(runner)
print('New cache-only candidate/runner prepared; original diagnostic unchanged.')
