// Uses real Chromium/Edge with a synthetic local form. Never opens real application accounts.
import {createRequire} from 'node:module';
import {readFile,mkdir,writeFile,cp} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import http from 'node:http';
import assert from 'node:assert/strict';
import {makeProfile,localPlan,validatePlan,exportSnapshot} from '../lib/core.mjs';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.JUNSHI_PLAYWRIGHT_MODULE||'playwright');
const extension=resolve(fileURLToPath(new URL('..',import.meta.url))),out=resolve(process.env.JUNSHI_TEST_OUTPUT||join(extension,'output/browser'));
await mkdir(out,{recursive:true});
const server=http.createServer(async(req,res)=>{res.setHeader('Content-Type','text/html;charset=utf-8');res.end(await readFile(join(extension,'tests/form.html')));});
await new Promise(r=>server.listen(0,'127.0.0.1',r));const url=`http://127.0.0.1:${server.address().port}`;
let browser,context,lastPanel;
const results=[];
try{
 browser=await chromium.launch({channel:process.env.JUNSHI_BROWSER_CHANNEL||'msedge',headless:true});context=await browser.newContext();
 const page=await context.newPage();await page.goto(url);
 await page.addScriptTag({path:join(extension,'lib/dom.js')});
 const snapshot=await page.evaluate(()=>JunshiDOM.scan());
 const structured={schema_version:'1',name:'林禾',contacts:['linhe@example.com','https://github.com/example'],sections:[{title:'教育经历',entries:[{title:'南城大学',subtitle:'软件工程',dates:'2021.09 - 2025.06',bullets:[]},{title:'北城大学',subtitle:'数据科学',dates:'',bullets:[]}]}]};
 const profile=makeProfile('姓名：林禾\n邮箱：linhe@example.com',{structured,name:'synthetic.json',sha:'a'.repeat(64)});profile.confirmed=true;
 const plan=localPlan(snapshot,profile),answers=validatePlan(plan,snapshot,profile);
 const result=await page.evaluate(req=>JunshiDOM.apply(req),{session_id:snapshot.session_id,answers});
 assert.equal(await page.locator('#name').inputValue(),'林禾');assert.equal(await page.locator('#school1').inputValue(),'南城大学');assert.equal(await page.locator('#school2').inputValue(),'北城大学');
 assert.equal(await page.locator('#start1').inputValue(),'2021-09');assert.equal(await page.locator('#missing-date').inputValue(),'');
 for(const id of ['why','salary','visa','otp','custom','passport-field'])assert.equal(await page.locator('#'+id).inputValue(),'');
 assert.equal(await page.locator('#phone').inputValue(),'本人原有号码');assert.equal(await page.locator('#consent').isChecked(),false);assert.equal(await page.evaluate(()=>submitted),0);
 assert.ok((await page.evaluate(()=>events)).includes('name'));results.push('native fields, repeated education, month precision, framework events, protected/existing fields, no submit');
 await page.locator('#name').fill('本人随后修正');await page.evaluate(()=>JunshiDOM.undo());assert.equal(await page.locator('#name').inputValue(),'本人随后修正');assert.equal(await page.locator('#school1').inputValue(),'');results.push('undo retains manual correction');
 const fresh=await page.evaluate(()=>JunshiDOM.scan());await page.evaluate(()=>document.getElementById('email').setAttribute('aria-label','新字段'));
 const stale=await page.evaluate(req=>JunshiDOM.apply(req),{session_id:fresh.session_id,answers:[{field_id:fresh.fields.find(f=>f.name==='email').id,value:'other@example.com'}]});assert.equal(stale[0].ok,false);results.push('stale DOM not filled');
 await page.screenshot({path:join(out,'form.png'),fullPage:true});
 await context.close();await browser.close();browser=null;
 // Extension integration uses a copied manifest with a localhost-only fixture grant.
 // The production activeTab click grant is not simulated or claimed tested here.
 const fixture=join(out,'extension-fixture');await cp(extension,fixture,{recursive:true,filter:p=>!p.startsWith(join(extension,'output'))&&!p.includes('/tests/')&&!p.includes('\\tests\\')});
 const manifest=JSON.parse(await readFile(join(fixture,'manifest.json'),'utf8'));manifest.host_permissions=['http://127.0.0.1/*'];await writeFile(join(fixture,'manifest.json'),JSON.stringify(manifest));
 context=await chromium.launchPersistentContext(join(out,'browser-profile-'+Date.now()),{channel:process.env.JUNSHI_BROWSER_CHANNEL||'msedge',headless:true,args:[`--disable-extensions-except=${fixture}`,`--load-extension=${fixture}`]});
 const worker=context.serviceWorkers()[0]||await context.waitForEvent('serviceworker',{timeout:20000});const extensionId=new URL(worker.url()).host;
 const form=await context.newPage();await form.goto(url);
 const panel=await context.newPage();lastPanel=panel;const errors=[];panel.on('pageerror',e=>errors.push(e.message));await panel.goto(`chrome-extension://${extensionId}/panel.html`);
 await panel.waitForFunction(()=>!document.querySelector('main').inert);
 await panel.setViewportSize({width:420,height:900});
 assert.equal(await panel.locator('#scan').isDisabled(),true);
 assert.equal(await panel.locator('#api-key').isVisible(),false);
 await panel.locator('#tab-fill').focus();await panel.keyboard.press('ArrowRight');
 assert.equal(await panel.locator('#tab-records').getAttribute('aria-selected'),'true');
 await panel.keyboard.press('End');assert.equal(await panel.locator('#tab-settings').getAttribute('aria-selected'),'true');
 await panel.keyboard.press('Home');assert.equal(await panel.locator('#tab-fill').getAttribute('aria-selected'),'true');
 await panel.screenshot({path:join(out,'ui-empty.png')});
 results.push('three accessible tabs, keyboard navigation, first-use action prerequisites, API settings outside daily flow');
 // Create synthetic text and image assets. No real CV is loaded into tests.
 const txt=join(out,'synthetic.txt');await writeFile(txt,'姓名：林禾\n邮箱：linhe@example.com\n学校：南城大学\n专业：软件工程');
 await panel.locator('#resume-file').setInputFiles(txt);await panel.waitForFunction(()=>document.getElementById('resume-meta').textContent.includes('synthetic.txt'));
 await panel.getByRole('button',{name:'确认这份简历，保存在本机',exact:true}).click();await panel.waitForFunction(()=>document.getElementById('resume-meta').textContent.includes('已确认'));
 // Route an actual extension message through its production service worker.
 const tabId=await worker.evaluate(async u=>(await chrome.tabs.query({})).find(t=>t.url?.startsWith(u)).id,url);
 const scanned=await panel.evaluate(id=>chrome.runtime.sendMessage({type:'scan',tabId:id}),tabId);
 assert.equal(scanned?.ok,true);
 const local=localPlan(scanned.result,await panel.evaluate(async()=>(await chrome.storage.local.get('profile')).profile));
 const filled=await panel.evaluate(data=>chrome.runtime.sendMessage(data),{type:'fill',tabId,data:{session_id:scanned.result.session_id,answers:local.answers}});assert.equal(filled.ok,true);assert.equal(await form.locator('#name').inputValue(),'林禾');results.push('real extension import/storage/service-worker fill with explicit localhost fixture permission');
 // OCR is run by packaged code/worker/WASM/language data. Verify no external request.
 const image=await form.evaluate(()=>{const c=document.createElement('canvas');c.width=1100;c.height=300;const x=c.getContext('2d');x.fillStyle='white';x.fillRect(0,0,c.width,c.height);x.fillStyle='black';x.font='38px Microsoft YaHei';x.fillText('姓名：林禾',35,70);x.fillText('邮箱：linhe@example.com',35,140);x.fillText('学校：南城大学',35,210);return c.toDataURL('image/png');});
 const imgPath=join(out,'synthetic.png');await writeFile(imgPath,Buffer.from(image.split(',')[1],'base64'));
 const external=[];context.on('request',r=>{if(/^https?:/.test(r.url())&&!r.url().startsWith(url))external.push(r.url());});
 await panel.locator('#use-ocr').check();await panel.locator('#resume-file').setInputFiles(imgPath);
 await panel.waitForFunction(()=>document.getElementById('resume-meta').textContent.includes('synthetic.png'),null,{timeout:120000});
 const ocrText=await panel.locator('#resume-text').inputValue();assert.match(ocrText,/linhe@example\.com/);assert.match(ocrText,/南城大学/);assert.equal(external.length,0);results.push('actual packaged Chinese/English OCR, no external requests');
 // PDF text layer path is tested separately from OCR.
 const pdfPage=await context.newPage();await pdfPage.setContent('<html><body style="font:24px Microsoft YaHei">姓名：林禾<br>邮箱：linhe@example.com<br>学校：南城大学</body></html>');const pdfPath=join(out,'synthetic.pdf');await pdfPage.pdf({path:pdfPath});await pdfPage.close();
 await panel.locator('#use-ocr').uncheck();await panel.locator('#resume-file').setInputFiles(pdfPath);await panel.waitForFunction(()=>document.getElementById('resume-meta').textContent.includes('synthetic.pdf'));
 assert.match(await panel.locator('#resume-text').inputValue(),/linhe@example\.com/);results.push('actual local PDF.js text extraction');
 // Exercise the production panel handlers against the fixture tab. The grant
 // remains localhost-only; this is not a substitute for a toolbar activation test.
 await panel.getByRole('button',{name:'确认这份简历，保存在本机',exact:true}).click();
 await panel.waitForFunction(()=>document.getElementById('resume-meta').textContent.includes('已确认'));
 await form.bringToFront();await panel.evaluate(()=>document.getElementById('scan').click());
 // The fixture's known values were already filled through the service worker;
 // this repeat scan must preserve them and report that nothing new was written.
 await panel.waitForFunction(()=>document.getElementById('status').textContent.startsWith('本轮没有可自动填写'));
 await panel.bringToFront();await panel.locator('#assistance > summary').click();await panel.getByText('复杂字段和开放题：交给现有军师',{exact:true}).click();
 const contextDownload=panel.waitForEvent('download');await panel.locator('#export-context').click();
 const contextFile=join(out,'junshi-form-context.json');await(await contextDownload).saveAs(contextFile);
 const handoff=JSON.parse(await readFile(contextFile,'utf8')),why=handoff.fields.find(f=>f.label==='为什么选择我们公司');
 assert.ok(why);const fillPlan={schema_version:'1',kind:'junshi-fill-plan',session_id:handoff.session_id,resume_sha256:handoff.resume_sha256,answers:[{field_id:why.id,value:'我希望把软件工程所学用于产品工作。',source_ids:[handoff.sources[0].id],kind:'draft'}]};
 await panel.locator('#plan-text').fill(JSON.stringify(fillPlan));await panel.evaluate(()=>document.getElementById('load-plan').click());
 await panel.waitForFunction(()=>document.getElementById('answers').querySelector('input[type=checkbox]'));
 assert.equal(await panel.locator('#fill-plan').isDisabled(),true);assert.equal(await form.locator('#why').inputValue(),'');
 assert.equal(await panel.locator('#answers input[type=checkbox]').isChecked(),false);
 await panel.locator('#answers input[type=checkbox]').check();await panel.locator('#fill-plan').click();
 await form.waitForFunction(()=>document.getElementById('why').value==='我希望把软件工程所学用于产品工作。');
 assert.equal(await form.evaluate(()=>submitted),0);results.push('production panel scan/export/import; draft remains empty until individually reviewed; no submit');
 await panel.locator('#tab-records').click();await panel.locator('#company').fill('合成公司');await panel.locator('#role').fill('合成AI产品岗');
 await panel.locator('#save-job').click();await panel.waitForFunction(()=>document.getElementById('status').textContent.startsWith('已收藏'));
 let saved=await panel.evaluate(async()=>(await chrome.storage.local.get('records')).records);assert.equal(saved[0].events.at(-1).status,'saved');
 await panel.locator('#record-editor > summary').click();await panel.locator('#used-resume').check();await panel.locator('#submitted').click();
 await panel.waitForFunction(()=>document.getElementById('status').textContent.startsWith('已记下'));
 saved=await panel.evaluate(async()=>(await chrome.storage.local.get('records')).records);
 assert.equal(saved[0].events.at(-1).status,'submitted');assert.equal(saved[0].events.at(-1).resume.name,'synthetic.pdf');assert.equal(saved[0].events.at(-1).submitted_at,'unknown');
 await panel.locator('#records details > summary').click();await panel.getByRole('button',{name:'记录反馈',exact:true}).click();
 await panel.waitForFunction(()=>document.getElementById('status').textContent.startsWith('反馈已记录'));
 assert.match(await panel.locator('#records').textContent(),/原投简历：synthetic.pdf/);
 await panel.locator('#search').fill('不存在的合成岗位');assert.match(await panel.locator('#records').textContent(),/没有找到匹配/);await panel.locator('#search').fill('');
 results.push('inline recruiting feedback preserves the original resume label; empty search state');
 await writeFile(join(out,'junshi-career-context.json'),JSON.stringify(await exportSnapshot(saved[0]),null,2));results.push('bookmark versus explicit submission; original attachment receipt; existing Junshi snapshot exported');
 assert.equal(external.length,0);
 assert.deepEqual(errors,[]);await panel.setViewportSize({width:420,height:900});
 assert.equal(await panel.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
 await panel.screenshot({path:join(out,'ui-records.png')});
 await panel.locator('#tab-fill').click();await panel.evaluate(()=>document.querySelector('main').scrollTop=0);await panel.screenshot({path:join(out,'panel.png')});
 await panel.locator('#tab-settings').click();await panel.screenshot({path:join(out,'ui-settings.png')});
 for(const width of [320,420]){await panel.setViewportSize({width,height:760});for(const name of ['fill','records','settings']){await panel.locator('#tab-'+name).click();assert.equal(await panel.evaluate(()=>document.documentElement.scrollWidth<=innerWidth&&document.querySelector('main').scrollWidth<=document.querySelector('main').clientWidth),true);}}
 assert.equal(await panel.evaluate(()=>document.querySelector('main').getBoundingClientRect().bottom<=document.querySelector('.feedback').getBoundingClientRect().top),true);
 results.push('320/420px panes have no horizontal overflow; feedback occupies its own row rather than covering content');
 await writeFile(join(out,'result.json'),JSON.stringify({passed:results,limitations:['Synthetic pages, not real employer acceptance','ActiveTab user toolbar activation not tested; integration fixture uses localhost-only host permission','OCR correctness only checked on the synthetic fixture']},null,2));
 console.log(JSON.stringify({passed:results,output:out}));
}catch(error){
 if(lastPanel&&!lastPanel.isClosed()){
  await lastPanel.screenshot({path:join(out,'failure.png'),fullPage:true});
  const diagnostics=await lastPanel.evaluate(()=>({status:document.getElementById('status')?.textContent,meta:document.getElementById('resume-meta')?.textContent}));
  await writeFile(join(out,'failure.json'),JSON.stringify({error:error.message,...diagnostics},null,2));console.error(diagnostics);
 }
 throw error;
}finally{await context?.close();await browser?.close();server.close();}
