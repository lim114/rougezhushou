"""Background native client pipe, via the user's existing Node bridge modules."""
import json
import msvcrt
import os
import queue
import shutil
import subprocess
import threading
import uuid
from pathlib import Path

def node_executable():
    found=shutil.which('node')
    if found:
        return found
    runtime=Path(os.environ.get('USERPROFILE',''))/'.cache/codex-runtimes'
    candidates=list(runtime.glob('*/dependencies/node/bin/node.exe'))
    if candidates:
        return str(candidates[0])
    raise FileNotFoundError('未找到 Node.js。需要 Node.js 22 或以上版本。')

class DesktopBackend:
    def __init__(self,data_dir,on_state):
        self.data_dir=Path(data_dir)
        self.on_state=on_state
        self.process=None
        self.pending={}
        self.lock=threading.Lock()
        self.write_lock=threading.Lock()
        self.instance_lock=None

    def start(self):
        if self.process is not None and self.process.poll() is None:
            return
        if self.instance_lock is None:
            self.data_dir.mkdir(parents=True,exist_ok=True)
            guard=(self.data_dir/'backend.lock').open('a+b')
            guard.seek(0)
            try:msvcrt.locking(guard.fileno(),msvcrt.LK_NBLCK,1)
            except OSError:
                guard.close()
                raise ConnectionError('另一份助手已连接聊天后台，请在已有窗口继续操作。') from None
            self.instance_lock=guard
        worker=Path(__file__).parent/'bridge/worker.cjs'
        self.process=subprocess.Popen([node_executable(),str(worker),str(self.data_dir)],
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,
            text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
        threading.Thread(target=self._read,args=(self.process,),daemon=True).start()

    def _read(self,process):
        try:
            for line in process.stdout:
                message=json.loads(line)
                if message.get('event')=='state':
                    self.on_state(message['state'])
                elif message.get('id'):
                    with self.lock:
                        item=self.pending.get(message['id'])
                        waiting=item[1] if item and item[0] is process else None
                        if waiting:self.pending.pop(message['id'],None)
                    if waiting:waiting.put(message)
        except (ValueError,OSError):
            pass
        finally:
            with self.lock:
                ids=[rid for rid,item in self.pending.items() if item[0] is process]
                waiting=[self.pending.pop(rid)[1] for rid in ids]
            for item in waiting:item.put({'error':'聊天后台连接已关闭；发送状态需读取确认，不会自动重发。'})

    def request(self,method,timeout=120,**arguments):
        with self.write_lock:
            self.start()
            rid=uuid.uuid4().hex
            waiting=queue.Queue()
            with self.lock:self.pending[rid]=(self.process,waiting)
            try:
                self.process.stdin.write(json.dumps({'id':rid,'method':method,**arguments},ensure_ascii=False)+'\n')
                self.process.stdin.flush()
            except (OSError,ValueError):
                with self.lock:self.pending.pop(rid,None)
                raise ConnectionError('聊天后台未收到确认；请刷新检查，不会自动重发。') from None
        try:
            response=waiting.get(timeout=timeout)
        except queue.Empty:
            with self.lock:self.pending.pop(rid,None)
            raise TimeoutError('客户端连接超时；如果正在发送，请刷新核对送达情况。') from None
        if response.get('error'):raise ConnectionError(response['error'])
        return response.get('result')

    def close(self):
        with self.write_lock:
            process=self.process
            if process is not None and process.poll() is None:
                try:
                    process.stdin.write('{"method":"close"}\n');process.stdin.flush()
                    process.stdin.close()
                except (OSError,ValueError):pass
            if self.instance_lock is not None:
                self.instance_lock.seek(0)
                try:msvcrt.locking(self.instance_lock.fileno(),msvcrt.LK_UNLCK,1)
                except OSError:pass
                self.instance_lock.close();self.instance_lock=None
