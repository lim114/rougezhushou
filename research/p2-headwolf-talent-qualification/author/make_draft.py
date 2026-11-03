import hashlib,pathlib
p=pathlib.Path(__file__).resolve().parent;f=p/'draft/rouge/operator_engine.py';b=f.read_bytes()
old=b"            head_interval=self.talent('\xe5\xa4\xb4\xe7\x8b\xbc','interval',20)\r\n"
new=old+b"            headwolf=op=='char_1038_whitw2' and '\xe5\xa4\xb4\xe7\x8b\xbc' in self.tv\r\n"
assert b.count(old)==1;b=b.replace(old,new)
for old,new in [(b"if op=='char_1038_whitw2' and time>=head_interval else 1)",b"if headwolf and time>=head_interval else 1)"),(b"if op=='char_1038_whitw2' and time>=3*head_interval else 0)",b"if headwolf and time>=3*head_interval else 0)")]:
 assert b.count(old)==1;b=b.replace(old,new)
f.write_bytes(b)
print(hashlib.sha256(b).hexdigest())
