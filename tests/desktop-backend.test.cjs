const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {ConversationHub}=require('../rouge/bridge/conversation-hub.cjs');
const pause=()=>new Promise(r=>setImmediate(r));

function receiptFixture(t){
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'rouge-receipt-'));
 let sends=0;
 const bridge={carrierThreadId:'fixture-carrier',
  read:async()=>({thread:{id:'fixture-target',kind:'chatgpt',status:'idle'},turns:sends?[{id:'fixture-turn',status:'completed',items:[{type:'userMessage',content:[{type:'text',text:'question'}]},{type:'agentMessage',phase:'final',text:'fixture answer'}]}]:[]}),
  send:async()=>{sends++;return {ok:true}}};
 const file=path.join(dir,'conversations.json'),hub=new ConversationHub({bridge,file});
 hub.states.chat.threadId='fixture-target';
 t.after(()=>{hub.close();fs.rmSync(dir,{recursive:true,force:true})});
 return {hub,file,pending:file+'.pending',sends:()=>sends};
}

test('receipt failure before any delivery releases the unsent operation',async t=>{
 const f=receiptFixture(t);fs.mkdirSync(f.pending);f.hub.states.chat.output='previous answer';
 await assert.rejects(f.hub.send('chat','question'),/回执/);
 const state=f.hub.snapshot().states.chat;
 assert.equal(f.sends(),0);assert.equal(state.running,false);assert.equal(state.pending,false);
 assert.equal(state.output,'previous answer');
 assert.equal(f.hub.operations.has('fixture-target'),false);assert.match(state.progress,/未发送/);
 fs.rmdirSync(f.pending);
 await f.hub.send('chat','question');await pause();
 assert.equal(f.sends(),1);assert.equal(f.hub.snapshot().states.chat.output,'fixture answer');
});

test('corrupt receipts remain intact and block delivery until explicitly repaired',async t=>{
 const f=receiptFixture(t),original='{unfinished receipt';fs.writeFileSync(f.pending,original);
 f.hub.recover();assert.match(f.hub.snapshot().error,/回执/);
 await assert.rejects(f.hub.send('chat','question'),/回执/);
 assert.equal(f.sends(),0);assert.equal(fs.readFileSync(f.pending,'utf8'),original);
 assert.equal(f.hub.snapshot().states.chat.running,false);
 fs.writeFileSync(f.pending,'{}'); // Explicit simulated repair of a temporary fixture only.
 await f.hub.send('chat','question');await pause();assert.equal(f.sends(),1);
});

test('invalid receipt containers cannot be silently overwritten',async t=>{
 const f=receiptFixture(t);
 for(const raw of ['null','[]','{"chat":{"threadId":"fixture-target","text":"q","baselineIds":null}}']){
  fs.writeFileSync(f.pending,raw);await assert.rejects(f.hub.send('chat','question'),/回执/);
  assert.equal(fs.readFileSync(f.pending,'utf8'),raw);assert.equal(f.sends(),0);
 }
});

test('a confirmed reply releases its operation even when receipt cleanup fails',async t=>{
 const f=receiptFixture(t),write=f.hub.writeReceipt.bind(f.hub);let writes=0;
 f.hub.writeReceipt=(...args)=>{if(++writes===2)throw Error('fixture readonly file');return write(...args)};
 await f.hub.send('chat','question');await pause();
 const state=f.hub.snapshot().states.chat;
 assert.equal(f.sends(),1);assert.equal(state.output,'fixture answer');assert.equal(state.running,false);
 assert.equal(f.hub.operations.has('fixture-target'),false);assert.match(state.error,/回执保存失败/);
 assert.equal(JSON.parse(fs.readFileSync(f.pending)).chat.text,'question');
 const restored=new ConversationHub({bridge:f.hub.bridge,file:f.file});restored.states.chat.threadId='fixture-target';restored.recover();
 assert.equal(restored.snapshot().states.chat.pending,true);await restored.read('chat');
 assert.equal(restored.snapshot().states.chat.pending,false);assert.equal(f.sends(),1);restored.close();
});

test('saving chat receipts preserves work receipts and unknown metadata',async t=>{
 const f=receiptFixture(t),work={threadId:'other-target',text:'other question',baselineIds:['old']};
 fs.writeFileSync(f.pending,JSON.stringify({work,metadata:null}));
 await f.hub.send('chat','question');await pause();
 assert.deepEqual(JSON.parse(fs.readFileSync(f.pending)),{work,metadata:null});
});
test('uncertain send is checked by reading its exact new turn, with no retry',async()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'rouge-chat-'));
 let sends=0,reads=0;
 const bridge={carrierThreadId:'fixture-carrier',
  list:async()=>({threads:[{id:'fixture-target',kind:'chatgpt',title:'fixture',status:'idle'}]}),
  read:async()=>({thread:{id:'fixture-target',kind:'chatgpt',status:'idle'},turns:++reads<=2?[]:[
   {id:'wrong-turn',status:'completed',items:[{type:'userMessage',content:[{type:'text',text:'other input'}]},{type:'agentMessage',phase:'final',text:'wrong answer'}]},
   {id:'matched-turn',status:'completed',items:[{type:'userMessage',content:[{type:'text',text:'question'}]},{type:'agentMessage',phase:'final',text:'matched answer'}]}]}),
  send:async()=>{sends++;throw Error('connection lost after delivery')}};
 const hub=new ConversationHub({bridge,file:path.join(dir,'conversations.json')});
 try{
  await hub.refresh();await hub.bind('chat','fixture-target');
  const sent=await hub.send('chat','question');
  for(let i=0;i<4;i++)await pause();
  assert.equal(sent.deliveryUncertain,true);assert.equal(sends,1);
  assert.equal(hub.snapshot().states.chat.output,'matched answer');
  assert.equal(hub.snapshot().states.chat.pending,false);
 }finally{hub.close();fs.rmSync(dir,{recursive:true,force:true})}
});
test('an observed but unfinished reply times out, preserves receipt and is not resent',async()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'rouge-chat-'));
 let now=0,sends=0,reads=0;
 const bridge={carrierThreadId:'fixture-carrier',
  list:async()=>({threads:[{id:'fixture-target',kind:'chatgpt',title:'fixture',status:'idle'}]}),
  read:async()=>({thread:{id:'fixture-target',kind:'chatgpt',status:'idle'},turns:++reads<=2?[]:[{id:'new-turn',status:'inProgress',items:[{type:'userMessage',content:[{type:'text',text:'question'}]}]}]}),
  send:async()=>{sends++;return {ok:true}}};
 const hub=new ConversationHub({bridge,file:path.join(dir,'conversations.json'),clock:()=>now,sleep:async()=>{now+=600001;await pause()}});
 try{
  await hub.refresh();await hub.bind('chat','fixture-target');await hub.send('chat','question');
  for(let i=0;i<10;i++)await pause();
  assert.equal(hub.snapshot().states.chat.running,false);
  assert.equal(hub.snapshot().states.chat.pending,true);
  assert.equal(sends,1);
  await assert.rejects(hub.send('chat','question'),/等待确认/);
  const recovered=new ConversationHub({bridge,file:path.join(dir,'conversations.json')});recovered.recover();
  assert.equal(recovered.snapshot().states.chat.pending,true);recovered.close();
 }finally{hub.close();fs.rmSync(dir,{recursive:true,force:true})}
});
