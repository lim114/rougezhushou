// Rouge integration: JSONL transport to the Python GUI; no foreground UI actions.
const fs=require('node:fs'),path=require('node:path'),readline=require('node:readline');
const {DesktopChat}=require('./desktop-chat.cjs');
const {ConversationHub}=require('./conversation-hub.cjs');
const dir=process.argv[2];
fs.mkdirSync(dir,{recursive:true});
const bridge=new DesktopChat({carrierThreadId:process.env.CODEX_THREAD_ID});
const hub=new ConversationHub({bridge,file:path.join(dir,'conversations.json')});
hub.recover();
const emit=message=>process.stdout.write(JSON.stringify(message)+'\n');
hub.on('change',()=>emit({event:'state',state:hub.snapshot()}));
const input=readline.createInterface({input:process.stdin});
input.on('line',async line=>{
 let command;
 try{
  command=JSON.parse(line);
  let result;
  switch(command.method){
   case 'refresh':result=await hub.refresh();hub.save();break;
   case 'bind':result=await hub.bind('chat',command.threadId);break;
   case 'read':result=await hub.read('chat');break;
   case 'send':result=await hub.send('chat',command.text);break;
   case 'snapshot':result=hub.snapshot();break;
   case 'close':hub.close();input.close();process.exit(0);return;
   default:throw Error('不支持的聊天后台操作');
  }
  emit({id:command.id,result:result??null});
 }catch(error){emit({id:command?.id,error:error.message})}
});
input.on('close',()=>{hub.close();process.exit(0)});
emit({event:'state',state:hub.snapshot()});
