import test from 'node:test';
import assert from 'node:assert/strict';
import {makeProfile,localPlan,validatePlan,blocked,keyFor,safeUrl,makeRecord,exportSnapshot,makeHandoff} from '../lib/core.mjs';
const source={schema_version:'1',name:'林禾',contacts:['linhe@example.com'],sections:[{title:'教育经历',entries:[{title:'南城大学',subtitle:'软件工程',dates:'2021.09 - 2025.06',bullets:[]},{title:'北城大学',subtitle:'数据科学',dates:'预计 2027.02 毕业',bullets:[]}]},{title:'项目经历',entries:[{title:'团队课程原型',subtitle:'负责评测脚本，服务由队友实现',dates:'',bullets:[{text:'编写内部测试脚本，没有生产用户。',confidence:'SELF_REPORTED'},{text:'计划接入实时服务。',confidence:'PLANNED'}]}]}]};
function profile(){const p=makeProfile('林禾\n团队课程原型',{structured:source,name:'synthetic.json',sha:'a'.repeat(64)});p.confirmed=true;return p;}
function field(id,label,group='',index=0){return {id,label,group,group_index:index,supported:true,blocked:false,filled:false};}
function snapshot(fields){return {session_id:'synthetic-session',page:{url:'https://example.com/apply?id=1',title:'合成岗位'},fields};}
test('Repeated grouped education uses the actual corresponding entries; absent dates stay absent',()=>{
 const p=profile(),s=snapshot([field('a','学校','education',0),field('b','学校','education',1),field('c','开始时间','education',1)]),plan=localPlan(s,p);
 assert.deepEqual(plan.answers.map(x=>x.value),['南城大学','北城大学']);
 assert.equal(p.facts.some(f=>f.value.includes('计划接入')),false);
});
test('Ambiguous ungrouped repeated fields are not filled with the first entry',()=>{
 assert.equal(localPlan(snapshot([field('a','学校'),field('b','学校')]),profile()).answers.length,0);
});
test('Resume import retains original contribution and refuses unconfirmed use',()=>{
 const p=profile();assert.ok(p.facts.some(f=>f.value.includes('服务由队友实现')));
 p.confirmed=false;assert.throws(()=>localPlan(snapshot([field('a','姓名')]),p),/确认/);
});
test('Fact plans cannot fabricate values, reference unknown sources, or cross resume/session boundaries',()=>{
 const p=profile(),s=snapshot([field('a','姓名')]),plan=localPlan(s,p);assert.equal(validatePlan(plan,s,p)[0].value,'林禾');
 for(const edit of [x=>x.answers[0].value='独立作者',x=>x.answers[0].source_ids=['missing'],x=>x.session_id='old',x=>x.resume_sha256='b'.repeat(64)]){const copy=structuredClone(plan);edit(copy);assert.throws(()=>validatePlan(copy,s,p));}
});
test('Open answers require draft and actual sources; eligibility is never guessed',()=>{
 const p=profile(),s=snapshot([field('a','为什么选择我们公司'),field('b','签证及工作资格')]);
 assert.equal(localPlan(s,p).answers.length,0);
 const plan={schema_version:'1',kind:'junshi-fill-plan',session_id:s.session_id,resume_sha256:p.sha256,answers:[{field_id:'a',value:'我想用课程项目中的评测经验做产品工作。',source_ids:[p.facts[0].id],kind:'draft'}]};
 assert.equal(validatePlan(plan,s,p)[0].kind,'draft');plan.answers[0].field_id='b';assert.throws(()=>validatePlan(plan,s,p));
 for(const l of ['薪资预期','password','护照号码','visa sponsorship'])assert.equal(blocked(l),true);
});
test('URL normalization retains SPA job identity while removing tracking and secrets',()=>{
 assert.equal(safeUrl('https://example.com/#/job/22'),'https://example.com/#/job/22');
 assert.equal(safeUrl('https://example.com/apply?job=22&utm_source=x&token=secret'),'https://example.com/apply?job=22');
 assert.throws(()=>safeUrl('javascript:alert(1)'));assert.throws(()=>safeUrl('https://user:pass@example.com'));
});
test('Application confirmation is explicit; original resume survives later versions and duplicate clicks',()=>{
 const p=profile(),s=snapshot([]);let r=makeRecord(null,s,p,{status:'saved'});
 assert.throws(()=>makeRecord(r,s,p,{status:'interview'}));
 r=makeRecord(r,s,p,{status:'submitted'});const original=r.events.find(e=>e.status==='submitted');
 const next=makeRecord(r,s,{name:'R2',sha256:'b'.repeat(64)},{status:'submitted'});
 assert.equal(next.events.length,r.events.length);assert.equal(next.events.find(e=>e.status==='submitted').resume.sha256,original.resume.sha256);
 const snapshotOut=makeRecord(next,s,p,{status:'saved'});assert.equal(snapshotOut.events.at(-1).status,'submitted');
});
test('Junshi handoff is existing snapshot shape and does not export full resume or claim submission time precision',async()=>{
 const r=makeRecord(null,snapshot([]),null,{company:'合成公司',role:'产品岗',status:'submitted'}),out=await exportSnapshot(r);
 assert.equal(out.records[0].confidence,'SELF_REPORTED');assert.equal(out.records[0].source_fingerprint.length,64);
 assert.equal(out.records[0].source_ref,'https://example.com/apply?id=1');
 assert.match(out.records[0].summary,/时间未知/);assert.equal('profile'in out,false);assert.equal('text'in out,false);
});
test('Mixed aliases do not infer a fact key',()=>{
 assert.equal(keyFor({label:'姓名',name:'email'}),null);
 assert.equal(keyFor({label:'邮箱',name:'passport_number'}),null);
});
test('Handoff removes credential parameters and edited filling text retains original attachment receipt',()=>{
 const s=snapshot([]);s.page.url='https://example.com/apply?job=1&token=private';
 assert.equal(makeHandoff(s,profile()).page.url,'https://example.com/apply?job=1');
 const p=profile();p.sha256='b'.repeat(64);p.name+='（文字修订）';
 const e=makeRecord(null,s,p,{status:'submitted'}).events[0];
 assert.equal(e.resume.name,'synthetic.json');assert.equal(e.resume.sha256,'a'.repeat(64));assert.equal(e.resume.fill_profile_sha256,'b'.repeat(64));
});
