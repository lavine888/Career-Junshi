import test from 'node:test';
import assert from 'node:assert/strict';
import {apiConfig,PRESETS,permissionOrigin,buildAIContext,resolveAIPlan,completionBody,requestCompletion} from '../lib/api.mjs';
import {readAPI,saveAPI,removeAPI} from '../lib/api-settings.mjs';
import {makeProfile} from '../lib/core.mjs';
const config=apiConfig({provider:'deepseek',...PRESETS.deepseek});
function fixtures(){
 const profile=makeProfile('姓名：林禾\n邮箱：linhe@example.com\n学校：南城大学',{name:'synthetic.txt',sha:'a'.repeat(64)});profile.confirmed=true;
 const snapshot={session_id:'s',fields:[{id:'f1',label:'候选人称呼',type:'text',supported:true,filled:false},{id:'f2',label:'为什么申请',type:'textarea',supported:true,filled:false},{id:'f3',label:'手机号',supported:true,filled:true},{id:'f4',label:'邮箱',name:'passport_number',supported:true,filled:false}]};
 return {profile,snapshot};
}
test('Domestic presets and endpoint normalization do not accept secrets or insecure remote URLs',()=>{
 assert.equal(config.endpoint,'https://api.deepseek.com/chat/completions');assert.equal(config.model,'deepseek-flash');
 assert.equal(apiConfig({provider:'glm',...PRESETS.glm}).endpoint,'https://open.bigmodel.cn/api/paas/v4/chat/completions');
 assert.equal(apiConfig({endpoint:'http://127.0.0.1:8080/v1/',model:'local'}).endpoint,'http://127.0.0.1:8080/v1/chat/completions');
 assert.equal(permissionOrigin(apiConfig({endpoint:'http://127.0.0.1:8080',model:'local'})),'http://127.0.0.1/*');
 for(const endpoint of ['http://example.com','https://user:secret@example.com','https://example.com?key=secret','https://example.com/#key','javascript:alert(1)'])assert.throws(()=>apiConfig({endpoint,model:'x'}));
});
test('Default request contains descriptors, never resume values, JD, page URL or existing fields',()=>{
 const {profile,snapshot}=fixtures(),context=buildAIContext(snapshot,profile,{jd:'PRIVATE-JD'}),raw=JSON.stringify(completionBody(config,context));
 for(const value of ['林禾','linhe@example.com','南城大学','PRIVATE-JD'])assert.equal(raw.includes(value),false);
 assert.deepEqual(context.fields.map(f=>f.id),['f1']);assert.ok(context.sources.every(s=>!('value'in s)&&s.key!=='source'));
 assert.equal('page'in context,false);assert.equal(completionBody(config,context).thinking.type,'disabled');
});
test('Content mode is explicit and still omits protected or filled fields',()=>{
 const {profile,snapshot}=fixtures(),context=buildAIContext(snapshot,profile,{includeContent:true,jd:'合成JD'});
 assert.deepEqual(context.fields.map(f=>f.id),['f1','f2']);assert.ok(JSON.stringify(context).includes('林禾'));assert.equal(context.job_description,'合成JD');
 profile.confirmed=false;assert.throws(()=>buildAIContext(snapshot,profile));
});
test('Legacy cache revisions cannot enter either API mode even if already confirmed',()=>{
 const {profile,snapshot}=fixtures();delete profile.parser_revision;profile.confirmed=true;const before=JSON.stringify(profile);
 for(const includeContent of [false,true])assert.throws(()=>buildAIContext(snapshot,profile,{includeContent}),/重新导入原文件/);
 assert.equal(JSON.stringify(profile),before);
});
test('Model matches source IDs; cannot generate a replacement fact, reuse forbidden fields or mix histories',()=>{
 const {profile,snapshot}=fixtures(),context=buildAIContext(snapshot,profile),id=profile.facts.find(s=>s.key==='name').id;
 const result={mappings:[{field_id:'f1',source_id:id}],drafts:[]};assert.equal(resolveAIPlan(result,context,snapshot,profile)[0].value,'林禾');
 for(const mutate of [r=>r.mappings[0].value='独立创始人',r=>r.mappings[0].source_id='unknown',r=>r.mappings[0].field_id='f4',r=>r.drafts.push({field_id:'f2',value:'x',source_ids:[id]})]){const r=structuredClone(result);mutate(r);assert.throws(()=>resolveAIPlan(r,context,snapshot,profile));}
 const school=profile.facts.find(s=>s.key==='school');snapshot.fields[0].group='education';snapshot.fields[0].group_index=1;const c=buildAIContext(snapshot,profile);assert.throws(()=>resolveAIPlan({mappings:[{field_id:'f1',source_id:school.id}],drafts:[]},c,snapshot,profile),/经历/);
});
test('Content extraction and drafts require original text, known sources and suitable fields',()=>{
 const {profile,snapshot}=fixtures(),context=buildAIContext(snapshot,profile,{includeContent:true}),source=profile.facts.find(s=>s.key==='source');
 const r={mappings:[{field_id:'f1',source_id:source.id,excerpt:'林禾'}],drafts:[{field_id:'f2',value:'我想把项目经验用于产品工作。',source_ids:[source.id]}]};
 const answers=resolveAIPlan(r,context,snapshot,profile);assert.equal(answers[1].kind,'draft');assert.equal(answers[1].approved,undefined);
 r.mappings[0].excerpt='没有来源的成果';assert.throws(()=>resolveAIPlan(r,context,snapshot,profile));
});
function memoryStorage(){const stores={local:{},session:{}};return Object.fromEntries(Object.entries(stores).map(([name,data])=>[name,{async get(keys){keys=typeof keys==='string'?[keys]:keys;return structuredClone(Object.fromEntries(keys.filter(k=>k in data).map(k=>[k,data[k]])));},async set(value){Object.assign(data,structuredClone(value));},async remove(keys){for(const key of typeof keys==='string'?[keys]:keys)delete data[key];}}]));}
test('Keys default to session, persist only by choice, stay bound to endpoint, and can be erased',async()=>{
 const storage=memoryStorage();await saveAPI(storage,config,'synthetic-key');
 assert.equal((await storage.local.get('apiSecret')).apiSecret,undefined);assert.equal((await readAPI(storage)).key,'synthetic-key');
 await assert.rejects(saveAPI(storage,{...config,endpoint:'https://other.example'},''));
 await saveAPI(storage,{...config,rememberKey:true},'');assert.equal((await storage.session.get('apiSecret')).apiSecret,undefined);assert.equal((await readAPI(storage)).key,'synthetic-key');
 await saveAPI(storage,{...config,rememberKey:false},'');assert.equal((await storage.local.get('apiSecret')).apiSecret,undefined);
 await removeAPI(storage);assert.deepEqual(await readAPI(storage),{config:null,key:''});
});
const response=(content,{status=200,finish_reason='stop'}={})=>new Response(status===200?JSON.stringify({choices:[{finish_reason,message:{content}}]}):'DO NOT REFLECT synthetic-key',{status});
test('Bounded native requests use one POST, bearer headers, no redirects or cookies, and synthetic-only tests',async()=>{
 let calls=0;const result=await requestCompletion(config,'synthetic-key',null,{test:true,fetcher:async(url,init)=>{calls++;assert.equal(url,config.endpoint);assert.equal(init.headers.Authorization,'Bearer synthetic-key');assert.equal(init.redirect,'error');assert.equal(init.credentials,'omit');assert.equal(JSON.parse(init.body).max_tokens,64);assert.equal(init.body.includes('林禾'),false);return response('{"ok":true}');}});
 assert.equal(result.ok,true);assert.equal(calls,1);
});
test('Provider errors, blanks, malformed JSON and truncation fail without retries or response-body leakage',async()=>{
 for(const item of [()=>response('',{status:401}),()=>response('',{status:429}),()=>response(' '),()=>response('not-json'),()=>response('{"ok":true}',{finish_reason:'length'})]){let calls=0;await assert.rejects(requestCompletion(config,'synthetic-key',null,{test:true,fetcher:async()=>{calls++;return item();}}),e=>!e.message.includes('synthetic-key'));assert.equal(calls,1);}
 let calls=0;await assert.rejects(requestCompletion(config,'synthetic-key',null,{timeoutMs:10,fetcher:async(url,{signal})=>{calls++;return new Promise((resolve,reject)=>signal.addEventListener('abort',()=>reject(new Error('synthetic-key'))));}}),/超时/);assert.equal(calls,1);
});
