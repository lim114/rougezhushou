"""Public temporary offscreen measurement only; never edit production/native UI."""
import ast
from contextlib import ExitStack
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import traceback
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
os.environ['QT_QPA_PLATFORM'] = 'offscreen'


def pin(path):
    raw = path.read_bytes()
    return {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}


def size(value):
    return [value.width(), value.height()]


def public_graph():
    path = ROOT / 'tests/test_readable_map_047.py'
    tree = ast.parse(path.read_bytes())
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'graph')
    graph = ast.literal_eval(next(node.value for node in function.body if isinstance(node, ast.Return)))
    graph['nodes'][0].update(observed_type='“居民”据点', remembered_type='“居民”据点')
    graph['nodes'][0].pop('content', None); graph['nodes'][0].pop('prediction', None)
    graph['nodes'][1]['remembered_type'] = '“居民”据点'
    graph['nodes'][2].update(observed_type='不期而遇', content={'kind': 'event', 'title': '和平守卫者'})
    graph['nodes'][2].pop('prediction', None)
    return graph


def main():
    output = HERE / 'OFFSCREEN_CAPTURE_SCROLL_CANDIDATE.json'
    if output.exists():
        raise FileExistsError('Preserve first actual measurement.')
    counts = {name: 0 for name in ('game_enumeration', 'game_connect', 'game_capture', 'game_next_frame',
                                 'desktop_start', 'desktop_request', 'provider_chat', 'credential_read')}
    record = {'kind': 'PUBLIC_OFFSCREEN_GEOMETRY_DIAGNOSTIC_NOT_NATIVE_ACCEPTANCE',
              'live_source_modified': False, 'native_window_started': False, 'actual_unittest_runs': 0}
    failure = None
    cleanup = None
    sources = [ROOT / 'rouge/app.py', ROOT / 'rouge/node_catalog_view.py', ROOT / 'rouge/map_view.py']
    sources += sorted((ROOT / 'rouge').glob('*_view.py'))
    sources = sorted(set(sources))
    before = {path.relative_to(ROOT).as_posix(): pin(path) for path in sources}
    app = None
    window = None

    def blocked(name):
        def call(*_args, **_kwargs):
            counts[name] += 1
            raise AssertionError('External operation forbidden: ' + name)
        return call

    try:
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QApplication, QLabel, QWidget, QScrollArea
        from rouge import app as module
        from rouge.map_reporting import location
        app = QApplication([])
        assert app.platformName() == 'offscreen', 'Never open a native diagnostic window.'
        record.update(qpa=app.platformName(), style=app.style().objectName(),
                      font={'family': app.font().family(), 'point_size': app.font().pointSizeF()},
                      screen={'logical_dpi': app.primaryScreen().logicalDotsPerInch(),
                              'device_pixel_ratio': app.primaryScreen().devicePixelRatio()})

        class PublicWindow(module.MainWindow):
            def refresh_windows(self):
                self.windows.clear()

        with tempfile.TemporaryDirectory(prefix='rouge-291-offscreen-size-') as directory, ExitStack() as stack:
            temporary = Path(directory)
            for key, filename in (('ROOT', None), ('SETTINGS', 'settings.json'),
                                  ('OPERATOR_STATE', 'operators.json'), ('RUN_STATE', 'run.json')):
                stack.enter_context(patch.object(module, key, temporary if filename is None else temporary / filename))
            stack.enter_context(patch.object(module, 'list_game_windows', side_effect=blocked('game_enumeration')))
            for method, name in (('connect', 'game_connect'), ('capture', 'game_capture'), ('next_frame', 'game_next_frame')):
                stack.enter_context(patch.object(module.GameCapture, method, side_effect=blocked(name)))
            for method, name in (('start', 'desktop_start'), ('request', 'desktop_request')):
                stack.enter_context(patch.object(module.DesktopBackend, method, side_effect=blocked(name)))
            stack.enter_context(patch.object(module, 'stream_chat', side_effect=blocked('provider_chat')))
            stack.enter_context(patch.object(module, 'read_key', side_effect=blocked('credential_read')))
            window = PublicWindow(); tabs = window.centralWidget(); panel = window.node_catalog
            initial_run = deepcopy(window.run.state)
            graph = public_graph()
            window.map_nodes.blockSignals(True); window.map_nodes.clear(); window.map_nodes.addItem('请选择地图上的节点', None)
            for node in sorted(graph['nodes'], key=lambda row: (row['row'], row['col'])):
                window.map_nodes.addItem(location(node, graph['grid']['rows']), node['id'])
            window.map_nodes.blockSignals(False)
            window.map_view.set_map(graph, historical=False)
            panel.set_map_context(graph, {'floor': 4}, epoch=window.run.state['id'], historical=False)
            panel.kind.setCurrentIndex(panel.kind.findData('event')); panel.search.setText('和平守卫者')
            panel.list.setCurrentRow(next(index for index, entry in enumerate(panel.entries)
                if entry['kind'] == 'event' and entry['record']['id'] == 'community_group_019'))
            tabs.setCurrentWidget(panel)
            window.resize(1050, 720); window.show(); app.processEvents()

            def flush():
                for widget in (tabs, window):
                    widget.updateGeometry()
                    if widget.layout():
                        widget.layout().invalidate(); widget.layout().activate()
                app.processEvents()

            def widget_stats(widget):
                result = {'class': type(widget).__name__, 'object_name': widget.objectName(),
                          'minimum_size': size(widget.minimumSize()), 'minimum_size_hint': size(widget.minimumSizeHint()),
                          'size_hint': size(widget.sizeHint()), 'actual_size': size(widget.size()),
                          'vertical_policy': widget.sizePolicy().verticalPolicy().name,
                          'horizontal_policy': widget.sizePolicy().horizontalPolicy().name,
                          'hidden': widget.isHidden()}
                layout = widget.layout()
                if layout:
                    margins = layout.contentsMargins()
                    result['layout'] = {'class': type(layout).__name__, 'minimum_size': size(layout.minimumSize()),
                                        'size_hint': size(layout.sizeHint()), 'spacing': layout.spacing(),
                                        'margins': [margins.left(), margins.top(), margins.right(), margins.bottom()]}
                if isinstance(widget, QLabel):
                    result['label_text_prefix'] = widget.text()[:100]
                return result

            def layout_tree(layout, depth=0):
                if layout is None or depth > 4:
                    return []
                rows = []
                for index in range(layout.count()):
                    item = layout.itemAt(index)
                    row = {'index': index, 'minimum_size': size(item.minimumSize()), 'size_hint': size(item.sizeHint())}
                    if item.widget():
                        widget = item.widget(); row.update(widget_stats(widget))
                        if widget.layout():
                            row['children'] = layout_tree(widget.layout(), depth + 1)
                    elif item.layout():
                        row['layout_class'] = type(item.layout()).__name__
                        row['children'] = layout_tree(item.layout(), depth + 1)
                    else:
                        row['spacer'] = True
                    rows.append(row)
                return rows

            flush()
            record['baseline'] = {'window': widget_stats(window), 'tabs': widget_stats(tabs),
                'requested': [1050, 720], 'actual': size(window.size()), 'page_count': tabs.count(),
                'player_reading': size(panel.player_detail.size())}
            page_list = [(tabs.widget(index), tabs.tabText(index), tabs.tabIcon(index)) for index in range(tabs.count())]
            record['pages'] = [{'index': index, 'title': title, **widget_stats(page)}
                               for index, (page, title, _icon) in enumerate(page_list)]
            record['largest_page_layouts'] = [{'index': index, 'title': title,
                'layout_tree': layout_tree(page.layout())} for index, (page, title, _icon) in enumerate(page_list)
                if page.minimumSizeHint().height() >= 620]
            # This is a temporary widget-only candidate, never a production patch.
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
            assert tabs.count() == len(page_list)
            assert window.run.state == initial_run
            assert not window.auto.isChecked() and not window.timer.isActive()
            assert window.capture.target is None and window.desktop.process is None
            assert not any(counts.values())
            record['run_state_unchanged'] = True
            window.close(); app.processEvents()
        from qt_verification_cleanup import shutdown_verification_qt
        cleanup = shutdown_verification_qt()
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
        if app is not None:
            try:
                from qt_verification_cleanup import shutdown_verification_qt
                cleanup = shutdown_verification_qt()
            except BaseException as cleanup_error:
                record['cleanup_error'] = repr(cleanup_error)
    after = {path.relative_to(ROOT).as_posix(): pin(path) for path in sources}
    record.update(failure=failure, diagnostic_completed=failure is None, external_operation_attempts=counts,
                  cleanup=cleanup, source_sha256_before=before, source_sha256_after=after,
                  source_unchanged=before == after, original_native_window_not_started=True)
    with output.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'diagnostic_completed': record['diagnostic_completed'], 'qpa': record.get('qpa'),
                      'baseline': record.get('baseline'), 'external_attempts': counts,
                      'source_unchanged': before == after, 'failure': failure}, ensure_ascii=False))
    return 0 if failure is None and before == after else 1


if __name__ == '__main__':
    raise SystemExit(main())
