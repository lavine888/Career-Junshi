// Actual MV3 service worker -> loopback HTTP fixture -> review -> real DOM fill.
// No real provider credentials, candidate materials, employer sites or paid calls.
import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir,cp} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {join,resolve} from 'node:path';
import http from 'node:http';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url),{chromium}=require(process.env.JUNSHI_PLAYWRIGHT_MODULE||'playwright');
const root=resolve(fileURLToPath(new URL('..',import.meta.url))),out=resolve(process.env.JUNSHI_TEST_OUTPUT||join(root,'output/api-browser'));
await mkdir(out,{recursive:true});
let mode='success';const calls=[];
const html=(await readFile(join(root,'tests/form.html'),'utf8')).replace('</form>','<label>候选人称呼<input id="unknown-name" name="preferred-applicant"></label></form>');
const server=http.createServer(async(req,res)=>{
 if(req.url!=='/v1/chat/completions'){res.setHeader('Content-Type','text/html;charset=utf-8');res.end(html);return;}
 const chunks=[];for await(const chunk of req)chunks.push(chunk);const body=JSON.parse(Buffer.concat(chunks).toString('utf8'));
 calls.push(body);assert.equal(req.headers.authorization,'Bearer synthetic-key');
 if(mode==='slow')await new Promise(r=>setTimeout(r,150));
 res.setHeader('Content-Type','application/json');
 if(mode==='401'){res.statusCode=401;res.end(JSON.stringify({error:{message:'DO NOT REFLECT synthetic-key'}}));return;}
 let content;
 if(body.max_tokens===64)content={ok:true};
 else{
  const context=JSON.parse(body.messages.at(-1).content);
  if(context.mode==='mapping')content={mappings:[{field_id:context.fields.find(f=>f.label==='候选人称呼').id,source_id:context.sources.find(s=>s.key==='name').id}],drafts:[]};
  else content={mappings:[],drafts:[{field_id:context.fields.find(f=>f.label==='为什么选择我们公司').id,value:'我希望把已有项目经验用于产品工作。',source_ids:[context.sources.find(s=>s.key==='source').id]}]};
 }
 res.end(JSON.stringify({choices:[{finish_reason:'stop',message:{content:JSON.stringify(content)}}]}));
});
await new Promise(r=>server.listen(0,'127.0.0.1',r));const url=`http://127.0.0.1:${server.address().port}`;
let context,panel;const passed=[];
try{
 const fixture=join(out,'extension-fixture');await cp(root,fixture,{recursive:true,filter:p=>!p.startsWith(join(root,'output'))&&!p.includes('/tests/')&&!p.includes('\\tests\\')});
 const manifest=JSON.parse(await readFile(join(fixture,'manifest.json'),'utf8'));manifest.host_permissions=['http://127.0.0.1/*'];await writeFile(join(fixture,'manifest.json'),JSON.stringify(manifest));
 context=await chromium.launchPersistentContext(join(out,'profile-'+Date.now()),{channel:'msedge',headless:true,args:[`--disable-extensions-except=${fixture}`,`--load-extension=${fixture}`]});
 const worker=context.serviceWorkers()[0]||await context.waitForEvent('serviceworker'),id=new URL(worker.url()).host;
 const form=await context.newPage();await form.goto(url);
 panel=await context.newPage();const errors=[];panel.on('pageerror',e=>errors.push(e.message));await panel.goto(`chrome-extension://${id}/panel.html`);await panel.waitForFunction(()=>!document.querySelector('main').inert);
 await panel.setViewportSize({width:420,height:900});
 const resume=join(out,'synthetic.txt');await writeFile(resume,'姓名：林禾\n邮箱：linhe@example.com\n学校：南城大学\n项目：合成课程原型，由本人负责测试。');
 await panel.locator('#resume-file').setInputFiles(resume);await panel.waitForFunction(()=>document.getElementById('resume-meta').textContent.includes('synthetic.txt'));
 await panel.locator('#confirm-resume').click();await panel.waitForFunction(()=>document.getElementById('resume-meta').textContent.includes('已确认'));
 await form.bringToFront();await panel.evaluate(()=>document.getElementById('scan').click());await panel.waitForFunction(()=>document.getElementById('status').textContent.startsWith('已填'));await panel.bringToFront();
 await panel.locator('#tab-settings').click();await panel.locator('#api-provider').selectOption('glm');assert.equal(await panel.locator('#api-model').inputValue(),'glm-4.7-flash');await panel.locator('#api-provider').selectOption('deepseek');
 await panel.locator('#api-advanced > summary').click();
 await panel.locator('#api-endpoint').fill(url+'/v1');await panel.locator('#api-key').fill('synthetic-key');await panel.locator('#api-save').click();await panel.waitForFunction(()=>document.getElementById('status').textContent.startsWith('API 配置已保存'));
 assert.equal(calls.length,0);assert.equal(await panel.locator('#api-key').inputValue(),'');
 const secrets=await panel.evaluate(async()=>({local:await chrome.storage.local.get('apiSecret'),session:await chrome.storage.session.get('apiSecret')}));assert.equal(secrets.local.apiSecret,undefined);assert.ok(secrets.session.apiSecret);
 await panel.locator('#api-test').click();await panel.waitForFunction(()=>document.getElementById('status').textContent.startsWith('合成 JSON 连接测试通过'));
 assert.equal(calls.length,1);assert.equal(calls[0].thinking.type,'disabled');assert.equal(calls[0].model,'deepseek-flash');assert.equal(JSON.stringify(calls[0]).includes('林禾'),false);passed.push('domestic presets, saved session key, explicit synthetic test through real service-worker HTTP');
 await panel.locator('#tab-fill').click();await panel.locator('#assistance > summary').click();
 await panel.locator('#api-preview').click();await panel.waitForFunction(()=>!document.getElementById('api-request').hidden);
 assert.equal(calls.length,1);const preview=await panel.locator('#api-payload').textContent();for(const value of ['林禾','linhe@example.com','synthetic-key'])assert.equal(preview.includes(value),false);
 await panel.locator('#api-run').click();await panel.waitForFunction(()=>document.getElementById('status').textContent.startsWith('得到 1 项'));
 assert.equal(await form.locator('#unknown-name').inputValue(),'');assert.equal(calls.length,2);assert.equal(JSON.stringify(calls[1]).includes('林禾'),false);
 await panel.locator('#fill-plan').click();await form.waitForFunction(()=>document.getElementById('unknown-name').value==='林禾');passed.push('default mapping sends no resume values; preview is not a network call; source value stays local until reviewed fill');
 await panel.locator('#assistance > summary').click();await panel.locator('#api-content').check();await panel.locator('#api-preview').click();await panel.waitForFunction(()=>!document.getElementById('api-request').hidden);
 assert.equal((await panel.locator('#api-payload').textContent()).includes('林禾'),true);await panel.locator('#api-run').click();await panel.waitForFunction(()=>document.getElementById('status').textContent.startsWith('得到 1 项'));
 assert.equal(await panel.locator('#answers input[type=checkbox]').isChecked(),false);assert.equal(await panel.locator('#fill-plan').isDisabled(),true);assert.equal(await form.locator('#why').inputValue(),'');
 await panel.locator('#answers input[type=checkbox]').check();await panel.locator('#fill-plan').click();await form.waitForFunction(()=>document.getElementById('why').value==='我希望把已有项目经验用于产品工作。');assert.equal(await form.evaluate(()=>submitted),0);passed.push('content is sent only after opt-in and preview; generated draft requires individual review; no submission');
 await panel.waitForFunction(()=>document.querySelector('#answers textarea')?.readOnly===true);
 assert.equal(await panel.locator('#answers textarea').evaluate(e=>e.readOnly),true);
 mode='slow';const beforeConcurrent=calls.length;
 const parallel=await panel.evaluate(async()=>{const {apiConfig:config}=await chrome.storage.local.get('apiConfig');return Promise.all([1,2].map(()=>chrome.runtime.sendMessage({type:'api-test',data:{endpoint:config.endpoint,model:config.model}})));});
 assert.equal(parallel.filter(r=>r.ok).length,1);assert.equal(parallel.filter(r=>r.error?.includes('进行中')).length,1);assert.equal(calls.length,beforeConcurrent+1);passed.push('concurrent extension requests allow only one provider call');
 await panel.locator('#tab-settings').click();
 mode='401';const before=calls.length;await panel.locator('#api-test').click();await panel.waitForFunction(()=>document.getElementById('status').textContent.includes('HTTP 401'));assert.equal(calls.length,before+1);assert.equal((await panel.locator('#status').textContent()).includes('synthetic-key'),false);passed.push('401 is shown without response-body/key leakage or automatic retries');
 assert.equal(await panel.locator('.feedback').getAttribute('data-tone'),'error');
 await panel.locator('#tab-records').click();await panel.locator('#backup-tools > summary').click();
 const download=panel.waitForEvent('download');await panel.locator('#backup').click();const backup=join(out,'backup.json');await(await download).saveAs(backup);assert.equal((await readFile(backup,'utf8')).includes('synthetic-key'),false);
 await panel.locator('#tab-fill').click();await panel.locator('#resume-review > summary').click();await panel.locator('#resume-raw > summary').click();await panel.locator('#resume-text').fill('姓名：林禾\n本次修改尚未确认');
 const beforeEdit=calls.length;assert.equal(await panel.locator('#api-preview').isDisabled(),true);assert.equal(await panel.locator('#scan').isDisabled(),true);assert.equal(calls.length,beforeEdit);passed.push('editing recognized text invalidates consent and prevents sending the old profile');
 await panel.locator('#tab-settings').click();
 await panel.locator('#api-clear').click();await panel.waitForFunction(()=>document.getElementById('api-state').textContent.startsWith('尚未配置'));
 const cleared=await panel.evaluate(async()=>({local:await chrome.storage.local.get(['apiConfig','apiSecret']),session:await chrome.storage.session.get('apiSecret')}));assert.deepEqual(cleared,{local:{},session:{}});passed.push('keys excluded from application backup; API configuration and both key stores erased');
 await panel.setViewportSize({width:420,height:900});await panel.evaluate(()=>document.querySelector('main').scrollTop=0);assert.equal(await panel.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);assert.deepEqual(errors,[]);await panel.screenshot({path:join(out,'api-panel.png')});
 await writeFile(join(out,'result.json'),JSON.stringify({passed,requests:calls.length,limitations:['Loopback API fixture, not a real domestic provider or model-quality test','Localhost fixture grant; actual toolbar activeTab/optional API permission prompts not automated']},null,2));console.log(JSON.stringify({passed,requests:calls.length}));
}catch(error){if(panel&&!panel.isClosed()){await panel.screenshot({path:join(out,'failure.png'),fullPage:true});console.error(await panel.locator('#status').textContent());}throw error;}
finally{await context?.close();server.close();}
