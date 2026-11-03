"""Run the existing assistant with explicit local-only Gate 0 instrumentation."""
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import argparse
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description='本机会话记录；不上传数据、不操作游戏。')
    parser.add_argument('--scenario', choices=('normal', 'transitions', 'resize'), required=True)
    parser.add_argument('--seconds', type=int, default=600)
    parser.add_argument('--auto-sample', action='store_true', help='开启现有后台只读自动采样')
    args = parser.parse_args()
    if not 1 <= args.seconds <= 3600:
        parser.error('--seconds 必须在1至3600之间')
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from rouge.app import MainWindow
    from rouge.session_recording import SessionRecorder, state_snapshot
    folder = ROOT/'.local/gate0'/f'{datetime.now():%Y%m%d-%H%M%S}-{args.scenario}-{uuid.uuid4().hex[:6]}'
    recorder = SessionRecorder(folder, scenario=args.scenario)
    recorder.event('runtime', python=sys.version.split()[0],
                   sources={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in (
                       'rouge/app.py','rouge/session_recording.py','rouge/player_game_map.py',
                       'rouge/capture.py','rouge/frame_buffer.py','rouge/recognition.py')})
    app = QApplication([])
    window = MainWindow(session_recorder=recorder)
    window.show_compact()
    recorder.event('state_baseline', state=state_snapshot(window.run.state))
    timer = QTimer(window)
    timer.setInterval(500)
    def observe():
        page = window.workspace.currentWidget()
        recorder.surfaces(app, entry=type(page).__name__ if page else None)
    timer.timeout.connect(observe)
    timer.start()
    def stop():
        timer.stop()
        recorder.close()
        window.session_recorder = None
        print('记录已结束，助手继续运行。记录目录：'+str(folder), flush=True)
    QTimer.singleShot(args.seconds*1000, stop)
    app.aboutToQuit.connect(recorder.close)
    if args.auto_sample:
        window.auto.setChecked(True)
    print('Gate 0 本地记录：'+str(folder), flush=True)
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
