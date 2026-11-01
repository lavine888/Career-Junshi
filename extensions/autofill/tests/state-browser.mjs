// Real extension/Edge regression for form targets, record provenance and review UI.
// Only synthetic resumes and localhost pages; no employer account or model API.
import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir,cp} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {join,resolve} from 'node:path';
import http from 'node:http';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.JUNSHI_PLAYWRIGHT_MODULE||'playwright');
const root=resolve(fileURLToPath(new URL('..',import.meta.url)));
const out=resolve(process.env.JUNSHI_TEST_OUTPUT||join(root,'output/state-browser'));
await mkdir(out,{recursive:true});
const pageHTML=path=>{
  const route=new URL(path,'http://fixture.local').pathname;
  const title=route==='/job/b'?'合成岗位 B':route==='/success'?'合成申请完成页':route==='/failed'?'合成全失败表单':route==='/partial'?'合成部分失败表单':'合成岗位 A';
  const nameLimit=['/failed','/partial'].includes(route)?' maxlength="1"':'';
  const email=route==='/failed'?'':`<label>电子邮箱<input id="email" name="email" type="email"></label>`;
  return `<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>${title}</title><style>body{font:16px 'Microsoft YaHei';max-width:700px;margin:30px auto}label{display:block;margin:14px}input,textarea{display:block;padding:8px;min-width:260px}</style><h1>${title}</h1><form id="application"><label>姓名<input id="name" name="full_name"${nameLimit}></label>${email}<label>为什么选择我们公司<textarea id="why"></textarea></label><button type="submit">提交申请</button></form><script>window.submitted=0;document.getElementById('application').onsubmit=e=>{e.preventDefault();submitted++};</script></html>`;
};
const server=http.createServer((req,res)=>{res.setHeader('Content-Type','text/html;charset=utf-8');res.end(pageHTML(req.url));});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const base=`http://127.0.0.1:${server.address().port}`;
const outcomes=[],errors=[],external=[];
let context,panel,form,panelURL;
const profile1=join(out,'synthetic-v1.txt'),profile2=join(out,'synthetic-v2.txt');
await writeFile(profile1,'姓名：林禾\n邮箱：linhe@example.com\n学校：南城大学\n专业：软件工程\n项目：合成课程原型，本人负责测试。');
await writeFile(profile2,'姓名：陈青\n邮箱：chenqing@example.com\n学校：北城大学\n专业：数据科学');
async function ready(){await panel.waitForFunction(()=>!document.querySelector('main').inert);}
async function tab(name){await panel.locator('#tab-'+name).click();await ready();}
async function openDetails(id){if(!await panel.locator('#'+id).evaluate(e=>e.open))await panel.locator('#'+id+' > summary').click();}
async function upload(file){await panel.locator('#resume-file').setInputFiles(file);const name=file.split(/[\\/]/).at(-1);await panel.waitForFunction(name=>document.getElementById('resume-meta').textContent.includes(name),name);await ready();}
async function confirm(){await panel.locator('#confirm-resume').click();await panel.waitForFunction(()=>document.getElementById('resume-meta').textContent.includes('已确认'));await ready();}
async function scan(){
  await tab('fill');await form.bringToFront();
  await panel.evaluate(()=>document.getElementById('scan').click());
  await panel.waitForFunction(()=>!document.getElementById('scan').hasAttribute('aria-busy')&&!document.querySelector('main').inert);
  await panel.bringToFront();
}
async function reset(route='/job/a'){
  await panel.evaluate(async()=>{await chrome.storage.local.clear();await chrome.storage.session.clear();});
  await form.goto(base+route);await panel.goto(panelURL);await ready();await upload(profile1);await confirm();await scan();
}
async function records(){return panel.evaluate(async()=>(await chrome.storage.local.get('records')).records||[]);}
async function changePage(path,title){await form.evaluate(({path,title})=>{history.pushState({},'',path);document.title=title;document.getElementById('why').value='';},{path,title});}
async function recordEditor(){await tab('records');await openDetails('record-editor');}
async function refreshRecord(){
  if(await panel.locator('#refresh-record-source').count())await panel.locator('#refresh-record-source').click();
  else await panel.locator('#save-job').click();
  await ready();
}
async function waitRecordCount(count){await panel.waitForFunction(async n=>((await chrome.storage.local.get('records')).records||[]).length===n,count);}
async function run(name,fn){
  try{await fn();outcomes.push({name,passed:true});}
  catch(error){outcomes.push({name,passed:false,error:error.message});if(panel&&!panel.isClosed())await panel.screenshot({path:join(out,`failure-${outcomes.length}.png`)});}
}
try{
  const fixture=join(out,'extension-fixture');
  await cp(root,fixture,{recursive:true,filter:p=>!p.startsWith(join(root,'output'))&&!p.includes('/tests/')&&!p.includes('\\tests\\')});
  const manifest=JSON.parse(await readFile(join(fixture,'manifest.json'),'utf8'));manifest.host_permissions=['http://127.0.0.1/*'];await writeFile(join(fixture,'manifest.json'),JSON.stringify(manifest));
  context=await chromium.launchPersistentContext(join(out,'profile-'+Date.now()),{channel:'msedge',headless:true,args:[`--disable-extensions-except=${fixture}`,`--load-extension=${fixture}`],viewport:{width:420,height:900}});
  context.on('request',request=>{if(/^https?:/.test(request.url())&&!request.url().startsWith(base))external.push(request.url());});
  const worker=context.serviceWorkers()[0]||await context.waitForEvent('serviceworker');
  panelURL=`chrome-extension://${new URL(worker.url()).host}/panel.html`;
  form=await context.newPage();await form.goto(base+'/job/a');panel=await context.newPage();panel.on('pageerror',error=>errors.push(error.message));await panel.goto(panelURL);await ready();

  await run('Changed active tab or same-tab page cannot receive the previously reviewed form plan',async()=>{
    await reset();await openDetails('assistance');await openDetails('manual-handoff');
    const download=panel.waitForEvent('download');await panel.locator('#export-context').click();const path=join(out,'form-context.json');await(await download).saveAs(path);
    const supplied=JSON.parse(await readFile(path,'utf8')),why=supplied.fields.find(f=>f.label==='为什么选择我们公司');
    assert.ok(why);
    const plan={schema_version:'1',kind:'junshi-fill-plan',session_id:supplied.session_id,resume_sha256:supplied.resume_sha256,answers:[{field_id:why.id,value:'合成原型中由本人负责测试。',source_ids:[supplied.sources.find(s=>s.key==='source').id],kind:'draft'}]};
    await panel.locator('#plan-text').fill(JSON.stringify(plan));await panel.locator('#load-plan').click();await ready();await panel.locator('#answers input[type=checkbox]').check();
    const other=await context.newPage();await other.goto(base+'/job/b');await other.bringToFront();
    try{
      await panel.evaluate(()=>document.getElementById('fill-plan').click());await ready();
      assert.equal(await form.locator('#why').inputValue(),'');assert.equal(await other.locator('#why').inputValue(),'');
      assert.match(await panel.locator('#status').textContent(),/切换|变化|重新识别/);
    }finally{await other.close();await panel.bringToFront();}
    await changePage('/job/b','合成岗位 B');await panel.locator('#fill-plan').click();await ready();
    assert.equal(await form.locator('#why').inputValue(),'');assert.equal(await form.evaluate(()=>submitted),0);
    assert.match(await panel.locator('#status').textContent(),/页面|网页|变化|切换|重新识别/);
  });
  await run('Changed record target blocks old attribution; choosing current clears role data and records B',async()=>{
    await reset();await recordEditor();await panel.locator('#company').fill('旧公司 A');await panel.locator('#role').fill('旧岗位 A');await panel.locator('#note').fill('旧岗位备注');await panel.locator('#used-resume').check();
    await changePage('/job/b','合成岗位 B');await refreshRecord();
    assert.equal((await records()).length,0,'A stale record must not be written before target review');
    assert.equal(await panel.locator('#record-source-warning').isVisible(),true);assert.equal(await panel.locator('#used-resume').isChecked(),false);
    await panel.locator('#record-source-current').click();await ready();
    for(const id of ['company','role','note'])assert.equal(await panel.locator('#'+id).inputValue(),'');
    assert.equal(await panel.locator('#used-resume').isChecked(),false);
    await panel.locator('#company').fill('合成公司 B');await panel.locator('#role').fill('合成产品岗位 B');await panel.locator('#submitted').click();await ready();await waitRecordCount(1);
    const saved=(await records())[0];assert.equal(saved.url,base+'/job/b');assert.equal(saved.company,'合成公司 B');assert.equal(saved.events.at(-1).status,'submitted');assert.equal(saved.events.at(-1).resume.name,'未关联');
    await panel.screenshot({path:join(out,'record-current.png')});
  });
  await run('Success page can explicitly retain original job; saving a note never claims it is unsubmitted',async()=>{
    await reset();await recordEditor();await panel.locator('#company').fill('合成公司 A');await panel.locator('#role').fill('合成产品岗位 A');await panel.locator('#used-resume').check();
    await changePage('/success','合成申请完成页');await refreshRecord();assert.equal((await records()).length,0);
    assert.equal(await panel.locator('#record-source-warning').isVisible(),true);await panel.screenshot({path:join(out,'record-source-warning.png')});
    await panel.locator('#record-source-keep').click();await ready();assert.equal(await panel.locator('#company').inputValue(),'合成公司 A');assert.equal(await panel.locator('#used-resume').isChecked(),false);
    await panel.locator('#used-resume').check();await panel.locator('#submitted').click();await ready();await waitRecordCount(1);
    let saved=(await records())[0];assert.equal(saved.url,base+'/job/a');assert.equal(saved.events.find(e=>e.status==='submitted').resume.name,'synthetic-v1.txt');
    await openDetails('record-editor');await panel.locator('#note').fill('补充合成备注');await panel.locator('#save-job').click();await ready();
    saved=(await records())[0];assert.equal(saved.events.at(-1).status,'submitted');assert.doesNotMatch(await panel.locator('#status').textContent(),/没有标为已投递|未投递/);
  });
  await run('New attachment, rescan and edited source each require a fresh used-resume confirmation',async()=>{
    await reset();await recordEditor();await panel.locator('#used-resume').check();await tab('fill');await upload(profile2);assert.equal(await panel.locator('#used-resume').isChecked(),false);
    await confirm();await recordEditor();await panel.locator('#used-resume').check();await scan();assert.equal(await panel.locator('#used-resume').isChecked(),false);
    await recordEditor();await panel.locator('#used-resume').check();await tab('fill');await openDetails('resume-review');await openDetails('resume-raw');await panel.locator('#resume-text').fill('姓名：陈青\n已修改但尚未确认');
    assert.equal(await panel.locator('#used-resume').isChecked(),false);assert.equal(await panel.locator('#scan').isDisabled(),true);
  });
  await run('Scanning a new target clears the previous role draft, JD and content consent',async()=>{
    await reset();await openDetails('assistance');await panel.locator('#jd').fill('仅属于旧岗位的合成 JD');await panel.locator('#api-content').check();
    await recordEditor();await panel.locator('#company').fill('旧公司');await panel.locator('#role').fill('旧岗位');await panel.locator('#note').fill('旧备注');await panel.locator('#used-resume').check();
    await changePage('/job/b','合成岗位 B');await scan();
    for(const id of ['company','role','note','jd','plan-text'])assert.equal(await panel.locator('#'+id).inputValue(),'');
    assert.equal(await panel.locator('#used-resume').isChecked(),false);assert.equal(await panel.locator('#api-content').isChecked(),false);
    await recordEditor();assert.match(await panel.locator('#record-page').textContent(),/合成岗位 B/);
  });
  await run('Zero and partial fill failures stay visible and are not presented as complete success',async()=>{
    await reset('/failed');
    assert.equal(await form.locator('#name').inputValue(),'');assert.equal(await panel.locator('#answer-details').evaluate(e=>e.open),true);assert.notEqual(await panel.locator('.feedback').getAttribute('data-tone'),'success');assert.match(await panel.locator('#answers').textContent(),/字数|限制|超出/);
    await panel.screenshot({path:join(out,'fill-zero-success.png')});
    await reset('/partial');assert.equal(await form.locator('#name').inputValue(),'');assert.equal(await form.locator('#email').inputValue(),'linhe@example.com');assert.equal(await panel.locator('#answer-details').evaluate(e=>e.open),true);assert.notEqual(await panel.locator('.feedback').getAttribute('data-tone'),'success');assert.match(await panel.locator('#status').textContent(),/需处理|未填|失败|1.*1/);
    await panel.screenshot({path:join(out,'fill-partial.png')});
  });
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
  const report={cases:outcomes,passed:outcomes.filter(item=>item.passed).length,failed:outcomes.filter(item=>!item.passed).length,limitations:['Synthetic localhost pages and supplied synthetic resume files only','Explicit localhost fixture host permission; production toolbar activation not automated','No live employer or model provider acceptance tested']};
  await writeFile(join(out,'result.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));if(report.failed)process.exitCode=1;
}finally{await context?.close();server.close();}
