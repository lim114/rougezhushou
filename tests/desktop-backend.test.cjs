const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {ConversationHub}=require('../rouge/bridge/conversation-hub.cjs');
const pause=()=>new Promise(r=>setImmediate(r));
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
