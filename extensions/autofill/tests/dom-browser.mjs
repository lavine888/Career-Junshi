// Focused real-browser regressions; only a synthetic loopback form is opened.
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {resolve,join} from 'node:path';
import {mkdir,writeFile} from 'node:fs/promises';
import http from 'node:http';
import assert from 'node:assert/strict';
import {makeProfile,localPlan,validatePlan} from '../lib/core.mjs';
const require=createRequire(import.meta.url),{chromium}=require(process.env.JUNSHI_PLAYWRIGHT_MODULE||'playwright');
const root=resolve(fileURLToPath(new URL('..',import.meta.url))),out=resolve(process.env.JUNSHI_TEST_OUTPUT||join(root,'output/dom-browser'));
await mkdir(out,{recursive:true});
const html=`<!doctype html><meta charset="utf-8"><title>合成字段回归</title>
<label>姓名<input id="name" style="outline:1px dotted red"></label>
<label>邮箱<input id="email"></label><label>电话<input id="phone"></label>
<fieldset><legend>教育经历</legend><label>学校<input id="school"></label><label>开始时间<input type="date" id="start"></label><label>结束时间<input type="month" id="end"></label></fieldset>`;
const server=http.createServer((req,res)=>{res.setHeader('Content-Type','text/html;charset=utf-8');res.end(html);});
await new Promise(r=>server.listen(0,'127.0.0.1',r));const url=`http://127.0.0.1:${server.address().port}`;
let browser,page;const passed=[];
try{
 browser=await chromium.launch({channel:'msedge',headless:true});page=await browser.newPage();
 async function fresh({legacy=false}={}){await page.goto(url+'/jobA');if(legacy)await page.evaluate(()=>{globalThis.JunshiDOM={scan(){throw Error('Legacy helper must be replaced');}};});await page.addScriptTag({path:join(root,'lib/dom.js')});return page.evaluate(()=>JunshiDOM.scan());}
 let snapshot=await fresh({legacy:true});assert.equal(await page.evaluate(()=>JunshiDOM.version),2);passed.push('an older injected helper is replaced after an extension update');
 const p=makeProfile('合成学历',{sha:'a'.repeat(64),structured:{schema_version:'1',sections:[{title:'教育经历',entries:[{title:'南城大学',dates:'2021.9.3 - 2025.6.30'}]}]}});p.confirmed=true;
 await page.evaluate(request=>JunshiDOM.apply(request),{session_id:snapshot.session_id,answers:validatePlan(localPlan(snapshot,p),snapshot,p)});
 assert.equal(await page.locator('#start').inputValue(),'2021-09-03');assert.equal(await page.locator('#end').inputValue(),'2025-06');passed.push('complete dates retain days; month controls use supplied year/month without inventing dates');
 snapshot=await fresh();
 const name=snapshot.fields.find(f=>f.label==='姓名');
 await page.evaluate(request=>JunshiDOM.apply(request),{session_id:snapshot.session_id,answers:[{field_id:name.id,value:'林禾'}]});
 assert.equal((await page.evaluate(()=>JunshiDOM.undo())).restored,1);assert.equal(await page.locator('#name').evaluate(e=>e.style.outline),'red dotted 1px');passed.push('same-field undo restores the original outline');
 snapshot=await fresh();
 let id=snapshot.fields.find(f=>f.label==='姓名').id;
 await page.evaluate(request=>JunshiDOM.apply(request),{session_id:snapshot.session_id,answers:[{field_id:id,value:'林禾'}]});
 await page.locator('#name').evaluate(e=>e.setAttribute('aria-label','新字段'));
 assert.equal((await page.evaluate(()=>JunshiDOM.undo())).restored,0);assert.equal(await page.locator('#name').inputValue(),'林禾');passed.push('undo does not erase a reused field with changed meaning');
 snapshot=await fresh();id=snapshot.fields.find(f=>f.label==='姓名').id;
 await page.evaluate(request=>JunshiDOM.apply(request),{session_id:snapshot.session_id,answers:[{field_id:id,value:'林禾'}]});
 await page.evaluate(()=>history.pushState({},'','/jobB'));
 assert.equal((await page.evaluate(()=>JunshiDOM.undo())).restored,0);assert.equal(await page.locator('#name').inputValue(),'林禾');passed.push('undo remains scoped to its original job URL');
 for(const change of ['route','scan']){
  snapshot=await fresh();
  await page.evaluate(change=>document.getElementById('email').addEventListener('input',()=>change==='route'?history.pushState({},'','/jobB'):JunshiDOM.scan(),{once:true}),change);
  const answers=[{field_id:snapshot.fields.find(f=>f.label==='邮箱').id,value:'linhe@example.com'},{field_id:snapshot.fields.find(f=>f.label==='电话').id,value:'12345678901'}];
  await assert.rejects(page.evaluate(request=>JunshiDOM.apply(request),{session_id:snapshot.session_id,answers}),/页面已经变化/);
  assert.equal(await page.locator('#phone').inputValue(),'');
 }
 passed.push('a route change or new scan during input events stops subsequent field writes');
 await writeFile(join(out,'result.json'),JSON.stringify({passed,limitations:['Synthetic loopback form, not employer acceptance or real model validation']},null,2));console.log(JSON.stringify({passed}));
}finally{await browser?.close();server.close();}
