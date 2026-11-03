const fs=require('node:fs'),crypto=require('node:crypto');
const parser=require(process.argv[2]);
const source=fs.readFileSync('.cache/event-statistics450/DVuI9Ou0.js');
const ast=parser.parse(source.toString('utf8'),{sourceType:'module'});
function literal(n){
 switch(n.type){
 case 'ObjectExpression':return Object.fromEntries(n.properties.map(p=>{if(p.type!=='ObjectProperty'||p.computed)throw Error('Not plain data');return[p.key.name??p.key.value,literal(p.value)]}));
 case 'ArrayExpression':return n.elements.map(literal);
 case 'StringLiteral':case 'NumericLiteral':case 'BooleanLiteral':return n.value;
 case 'TemplateLiteral':if(n.expressions.length===0)return n.quasis[0].value.cooked;break;
 case 'UnaryExpression':if(n.operator==='!'&&n.argument.type==='NumericLiteral'&&[0,1].includes(n.argument.value))return !n.argument.value;break;
 }
 throw Error('Unsupported data syntax:'+n.type);
}
const candidates=[];
for(const n of ast.program.body)if(n.type==='VariableDeclaration')for(const d of n.declarations)if(d.init?.type==='ObjectExpression'&&d.init.properties.some(p=>p.key?.name==='model'&&p.value.type==='TemplateLiteral'&&p.value.quasis[0].value.cooked==='joint-depletion-adjusted'))candidates.push(literal(d.init));
if(candidates.length!==1)throw Error('Expected one public aggregate table');
const data=candidates[0],sum=data.rows.reduce((s,r)=>s+r.observedCount,0),cohorts={};
for(const r of data.rows){const k=r.floor+':'+r.treehole;cohorts[k]=(cohorts[k]||0)+r.observedCount;}
const result={schema:'rouge-public-encounter-samples-v1',provider:'路标档案馆',source_url:'https://www.lubiao.wiki/nodes/encounters/rogue_6',dataset_url:'https://www.lubiao.wiki/_nuxt/DVuI9Ou0.js',retrieved_at:new Date().toISOString(),source_sha256:crypto.createHash('sha256').update(source).digest('hex'),metadata:Object.fromEntries(Object.entries(data).filter(([k])=>k!=='rows')),rows:data.rows};
fs.writeFileSync('.cache/event-statistics450/samples.json',JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({rows:data.rows.length,declared_observations:data.observations,observed_count_sum:sum,cohorts,parser_version:require(process.argv[2]+'/package.json').version}));
