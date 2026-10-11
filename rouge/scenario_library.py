"""Private offline scenarios; opening never restores account or run state."""
import hashlib, json, os, tempfile, uuid
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
from .damage import calculate_damage
from .manual_scenario import parse_preview_object
from .technology_state import _timestamp

MAX_BYTES = 1048576


def check_json_structure(value):
    pending = [(value,0)]
    while pending:
        item,depth = pending.pop()
        if depth>64: raise ValueError('局外情景的JSON层级不能超过64层。')
        if isinstance(item,dict):
            if any(type(key) is not str for key in item): raise ValueError('局外情景字段名需要JSON文字。')
            pending.extend((child,depth+1) for child in item.values())
        elif isinstance(item,list): pending.extend((child,depth+1) for child in item)
        elif type(item) not in (str,int,float,bool,type(None)): raise ValueError('局外情景需要JSON条件。')


def model_signature():
    """Fingerprint installed public calculation code/data, never private files."""
    root = Path(__file__).parent; digest = hashlib.sha256()
    paths = sorted([*root.rglob('*.py'), *(root/'data').rglob('*.json')])
    for path in paths:
        digest.update(path.relative_to(root).as_posix().encode('utf-8'))
        digest.update(b'\0'); digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def scenario_name(value):
    if type(value) is not str: raise ValueError('情景名称需要文字。')
    name = value.strip()
    if not 1 <= len(name) <= 60 or any(ord(c)<32 or 0xd800<=ord(c)<=0xdfff for c in name):
        raise ValueError('情景名称需要1–60个可显示字符。')
    return name


class ScenarioLibrary:
    def __init__(self,path=None):
        self.path = Path(path) if path is not None else None
        self._state = {'schema_version':1,'topic_id':'rogue_6','records':{}}
        self._expected_hash = None; self.issue = None
        if self.path is None: return
        try:
            if self.path.is_symlink(): raise ValueError('linked library')
            raw = self.path.read_bytes()
            if len(raw)>MAX_BYTES: raise ValueError('large library')
            state = parse_preview_object(raw.decode('utf-8'),'情景库'); check_json_structure(state); self._validate(state)
        except FileNotFoundError:
            try: self.path.lstat()
            except FileNotFoundError: return
            except OSError: pass
            self.issue = '原情景库路径不可用，已保留。'; return
        except (OSError,ValueError,RecursionError):
            self.issue = '原情景库不可用，已保留原文件。'; return
        self._state = state; self._expected_hash = hashlib.sha256(raw).hexdigest()

    def _validate(self,state):
        if type(state.get('schema_version')) is not int or state['schema_version']!=1 or state.get('topic_id')!='rogue_6':
            raise ValueError('unsupported scenario library')
        records = state.get('records')
        if not isinstance(records,dict) or len(records)>20: raise ValueError('invalid library records')
        names = set()
        for identity,record in records.items():
            if not identity or not isinstance(record,dict): raise ValueError('invalid library record')
            if record.get('kind') != 'manual_offline': continue  # Future types remain opaque.
            name = scenario_name(record.get('name')); signature = record.get('model_signature')
            if (name!=record['name'] or name in names or not isinstance(record.get('scenario'),dict) or
                    not _timestamp(record.get('saved_at')) or type(signature) is not str or len(signature)!=64 or
                    any(c not in '0123456789abcdef' for c in signature)):
                raise ValueError('invalid offline scenario')
            names.add(name)

    def snapshot(self): return deepcopy(self._state)

    def records(self):
        return [{**deepcopy(record),'id':identity} for identity,record in self._state['records'].items()
                if record.get('kind')=='manual_offline']

    def get(self,identity):
        if type(identity) is not str: raise ValueError('请选择已保存的局外情景。')
        record = self._state['records'].get(identity)
        if record is None or record.get('kind')!='manual_offline': raise ValueError('请选择已保存的局外情景。')
        return {**deepcopy(record),'id':identity}

    def save_new(self,name,scenario):
        name = scenario_name(name)
        if len(self._state['records'])>=20: raise ValueError('情景库最多20项，请先删除不需要的局外情景。')
        if any(record['name']==name for record in self.records()): raise ValueError('已有同名情景，请更换名称。')
        check_json_structure(scenario)
        # Strict JSON round trip preserves text and opaque conditions; no pickle/eval.
        try: payload = json.dumps(scenario,ensure_ascii=True,allow_nan=False)
        except (TypeError,ValueError,OverflowError): raise ValueError('情景需要有限JSON条件。') from None
        if len(payload.encode('utf-8'))>MAX_BYTES: raise ValueError('情景内容过大。')
        copied = parse_preview_object(payload,'局外情景')
        try: calculate_damage(deepcopy(copied))
        except (KeyError,TypeError) as error: raise ValueError('情景条件不可测算：'+str(error)) from None
        identity = uuid.uuid4().hex
        record = {'kind':'manual_offline','name':name,'scenario':copied,
                  'saved_at':datetime.now(timezone.utc).isoformat(),'model_signature':model_signature()}
        candidate = deepcopy(self._state); candidate['records'][identity] = record
        check_json_structure(candidate)
        if len(json.dumps(candidate,ensure_ascii=True,indent=2,allow_nan=False).encode('utf-8'))>MAX_BYTES:
            raise ValueError('情景库内容过大，请先删除不需要的局外情景。')
        self._state = candidate; self.save(); return identity

    def delete(self,identity):
        self.get(identity); del self._state['records'][identity]; return self.save()

    def persistence_notice(self):
        if self.issue: return self.issue+' 本次编辑仅在当前窗口有效，不会覆盖原情景库。'
        if self.path is None: return '临时情景库，关闭后不保留。'
        return '局外情景单独保存，开始新局后仍保留；不会载入账号或本局。'

    def save(self):
        if self.issue: return False
        if self.path is None: return True
        temporary = None
        try:
            self._validate(self._state)
            if self.path.is_symlink(): raise ValueError('linked library')
            try: current = hashlib.sha256(self.path.read_bytes()).hexdigest()
            except FileNotFoundError:
                try: self.path.lstat()
                except FileNotFoundError: current = None
                else: raise ValueError('unreadable library')
            if current != self._expected_hash:
                self.issue = '情景库已被其他窗口或程序修改，原文件已保留。'; return False
            payload = (json.dumps(self._state,ensure_ascii=True,indent=2,allow_nan=False)+'\n').encode('utf-8')
            if len(payload)>MAX_BYTES: raise ValueError('large library')
            self.path.parent.mkdir(parents=True,exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=self.path.parent,prefix='scenario-',suffix='.tmp',delete=False) as output:
                temporary = Path(output.name); output.write(payload); output.flush(); os.fsync(output.fileno())
            os.replace(temporary,self.path); self._expected_hash = hashlib.sha256(payload).hexdigest(); return True
        except (OSError,ValueError):
            self.issue = '情景库保存未完成，原文件已保留。'; return False
        finally:
            if temporary is not None:
                try: temporary.unlink(missing_ok=True)
                except OSError: pass
