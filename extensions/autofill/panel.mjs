import {makeProfile,localPlan,validatePlan,makeHandoff,makeRecord,exportSnapshot,safeUrl,sha256,needsProfileRefresh} from './lib/core.mjs';
import {readResume} from './lib/read-resume.mjs';
import {PRESETS,apiConfig,permissionOrigin,buildAIContext,resolveAIPlan} from './lib/api.mjs';
import {readAPI,saveAPI,removeAPI} from './lib/api-settings.mjs';
const $=id=>document.getElementById(id);
let profile=null,snapshot=null,tabId=null,answers=[],records=[];
let apiPrepared=null;
let apiReady=false,canUndo=false,lastFillResults=[];
let recordPage=null,pendingRecordPage=null,recordAcknowledgedPage='';
const status=(s,tone='info')=>{$('status').textContent=s;document.querySelector('.feedback').dataset.tone=tone;};
const show=(tag,text,cls='')=>{const e=document.createElement(tag);e.textContent=text;e.className=cls;return e;};
// Resolve persisted state before registering an import/save action. An import may
// never race a late initial read and be replaced by an old profile or null.
try{const state=await chrome.storage.local.get(['profile','records']);profile=state.profile||null;records=state.records||[];if(needsProfileRefresh(profile))profile={...profile,confirmed:false};}
catch(e){status(e.message);}
async function save(){const changes={records};if(!needsProfileRefresh(profile))changes.profile=profile;await chrome.storage.local.set(changes);}
function bind(id,fn){$(id).addEventListener('click',async()=>{const b=$(id),main=document.querySelector('main'),previousInert=main.inert;main.inert=true;b.disabled=true;b.setAttribute('aria-busy','true');try{await fn();}catch(e){status(e.message,'error');}finally{main.inert=previousInert;b.disabled=false;b.removeAttribute('aria-busy');updateControls();}});}
function pageIdentity(page){return page?`${page.tabId}:${safeUrl(page.url)}`:'';}
function tabPage(tab){if(!tab||!/^https?:\/\//.test(tab.url||''))throw Error('请在招聘网页点击扩展图标，授予本次网页访问权限后重试。');return {tabId:tab.id,url:safeUrl(tab.url),title:(tab.title||'招聘网页').slice(0,200)};}
async function currentRecordPage(){
  const [active]=await chrome.tabs.query({active:true,currentWindow:true});
  if(active?.url?.startsWith(chrome.runtime.getURL(''))){
    const selected=recordPage?.tabId??tabId;
    if(selected===null||selected===undefined)throw Error('请先在招聘网页打开助手，或识别一次目标表单。');
    return tabPage(await chrome.tabs.get(selected));
  }
  return tabPage(active);
}
async function assertFormTarget(){
  if(tabId===null)throw Error('请先识别目标招聘表单。');
  const [active]=await chrome.tabs.query({active:true,currentWindow:true});
  if(active?.id!==tabId&&!active?.url?.startsWith(chrome.runtime.getURL('')))throw Error('当前网页已切换，请回到目标表单重新识别，旧方案未执行。');
  const target=await chrome.tabs.get(tabId);
  if(snapshot?.page&&target.url!==snapshot.page.url)throw Error('招聘网页已变化，请重新识别，旧方案未执行。');
}
async function message(type,data){await assertFormTarget();const r=await chrome.runtime.sendMessage({type,tabId,data});if(!r?.ok)throw Error(r?.error||'无法操作当前表单，请回到网页重新点击扩展。');return r.result;}
function clearRecordDraft(){for(const id of ['company','role','note','jd','plan-text'])$(id).value='';$('used-resume').checked=false;$('api-content').checked=false;}
function selectRecordPage(page,{clear=false}={}){
  if(clear)clearRecordDraft();
  if(pageIdentity(page)!==pageIdentity(recordPage))$('used-resume').checked=false;
  recordPage=page;pendingRecordPage=null;recordAcknowledgedPage=pageIdentity(page);$('record-source-warning').hidden=true;updateControls();
}
function showRecordConflict(page){
  pendingRecordPage=page;$('used-resume').checked=false;$('record-source-warning').hidden=false;
  $('record-source-description').textContent=`原岗位：${recordPage.title}。当前网页：${page.title}。提交后的成功页可选择仍记原岗位；换了岗位则改用当前网页。`;
  updateControls();
}
async function refreshRecordPage(){
  const page=await currentRecordPage();
  if(!recordPage)selectRecordPage(page);
  else if(pageIdentity(page)!==pageIdentity(recordPage)&&pageIdentity(page)!==recordAcknowledgedPage)showRecordConflict(page);
  return page;
}
function download(name,value){const blob=new Blob([typeof value==='string'?value:JSON.stringify(value,null,2)],{type:name.endsWith('.json')?'application/json':'text/plain;charset=utf-8'});const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),30000);}
function renderProfile(){
  $('resume-meta').textContent=profile?`${profile.name} · ${profile.confirmed?'已确认':'待你检查确认'}${profile.ocr?' · OCR识别结果':''}`:'尚未导入简历';
  $('resume-text').value=profile?.text||'';
  const names={name:'姓名',email:'邮箱',phone:'电话',github:'GitHub',school:'学校',major:'专业',degree:'学位',start:'开始时间',end:'结束时间',project:'项目',project_description:'项目描述',role:'担任角色',contribution:'个人贡献',company:'公司',title:'职位'};
  const groups={education:'教育经历',project:'项目经历',work:'工作经历'};
  const legacy=needsProfileRefresh(profile),fields=legacy?[]:(profile?.facts||[]).filter(f=>f.key!=='source');
  if(legacy)$('resume-meta').textContent=profile.name+' · 旧解析缓存，仅供查看';
  $('resume-raw').querySelector('summary').textContent=legacy?'查看旧版识别原文':'查看或修正识别原文';
  const factRow=f=>{const row=show('div','','fact-row');row.append(show('dt',`${f.group?`${groups[f.group]||f.group} ${f.index+1} · `:''}${names[f.key]||f.key}`),show('dd',f.value));return row;};
  $('facts').replaceChildren(...fields.slice(0,6).map(factRow));
  if(profile&&!fields.length)$('facts').append(show('dd',legacy?'旧字段匹配仅作历史资料，不用于本次填写，请重新导入附件。':'未识别到常用字段，请展开原文核对。'));
  $('extra-facts').hidden=fields.length<=6;$('extra-facts-title').textContent=`查看其他识别字段（${Math.max(0,fields.length-6)} 项）`;$('extra-facts-list').replaceChildren(...fields.slice(6).map(factRow));
  $('resume-review').hidden=!profile;$('resume-review').open=!!profile&&!profile.confirmed;
  updateControls();
}
$('resume-file').addEventListener('change',async()=>{invalidateAPI();$('used-resume').checked=false;canUndo=false;document.querySelector('main').inert=true;try{status('正在读取…');profile=await readResume($('resume-file').files[0],{ocr:$('use-ocr').checked,progress:status});snapshot=null;answers=[];lastFillResults=[];renderAnswers();renderProfile();status('已本地识别，请展开检查文字，然后确认。');}catch(e){status(e.message,'error');}finally{document.querySelector('main').inert=false;}});
$('resume-text').addEventListener('input',()=>{if(!profile)return;profile.confirmed=false;$('used-resume').checked=false;invalidateAPI();answers=[];renderAnswers();$('resume-meta').textContent=profile.name+' · 文字已修改，请更新并重新确认';updateControls();});
bind('reparse',async()=>{invalidateAPI();if(!profile)throw Error('请先导入简历。');if(needsProfileRefresh(profile))throw Error('解析方式已更新，请重新导入原文件，不能直接沿用旧字段。');$('used-resume').checked=false;canUndo=false;lastFillResults=[];const text=$('resume-text').value,old=profile;profile=makeProfile(text,{name:old.name+'（文字修订）',sha:await sha256(text),ocr:old.ocr});profile.file_name=old.file_name||old.name;profile.file_sha256=old.file_sha256||old.sha256;snapshot=null;answers=[];renderAnswers();renderProfile();status('已更新填表文字，旧方案已失效；原附件文件指纹保留，请确认资料。');});
bind('confirm-resume',async()=>{if(!profile)throw Error('请先导入简历。');if(needsProfileRefresh(profile))throw Error('解析方式已更新，请重新导入原文件。');if($('resume-text').value!==profile.text)throw Error('识别文字已修改，请先点击“按修改后的文字更新”。');profile.confirmed=true;await save();renderProfile();status('这份简历已确认并保存在当前浏览器本机。');});
bind('scan',async()=>{
  invalidateAPI();
  if(!profile?.confirmed)throw Error('请先确认本次简历。');
  status('正在识别当前页面，填写有来源的空白项…','busy');
  const [tab]=await chrome.tabs.query({active:true,currentWindow:true});tabId=tab.id;
  const selected=tabPage(tab),changed=recordPage&&pageIdentity(recordPage)!==pageIdentity(selected);
  snapshot=null;answers=[];lastFillResults=[];canUndo=false;$('used-resume').checked=false;
  snapshot=await message('scan');selectRecordPage(selected,{clear:!!changed});renderAnswers();
  $('page-title').textContent=snapshot.page.title;
  const plan=localPlan(snapshot,profile);answers=validatePlan(plan,snapshot,profile);renderAnswers();
  const result=await message('fill',{session_id:snapshot.session_id,answers});
  for(const r of result){const a=answers.find(x=>x.field_id===r.id);if(a)a.result=r;}
  reflectFill(result);renderAnswers();reportFill(result);
});
bind('undo',async()=>{const result=await message('undo');canUndo=false;invalidateAPI();snapshot=await message('scan',{keepHistory:true});answers=[];lastFillResults=[];renderAnswers();renderFillSummary();status(`已撤销 ${result.restored} 项；你手动改过的内容保留。`,'success');});
bind('export-context',async()=>{if(!snapshot||!profile?.confirmed)throw Error('先识别当前页并确认简历。');await assertFormTarget();download('junshi-form-context.json',makeHandoff(snapshot,profile,$('jd').value));status('已导出当前表单和必要简历来源。把文件交给现有军师，生成junshi-fill-plan再导入。');});
function loadPlan(raw){
  invalidateAPI();
  if(!snapshot)throw Error('请先识别当前表单。');
  if(raw.length>500000)throw Error('方案文件过大。');
  const parsed=JSON.parse(raw.trim().replace(/^```(?:json)?\s*/,'').replace(/\s*```$/,''));
  answers=validatePlan(parsed,snapshot,profile);renderAnswers();revealAnswers();status('方案已检查。请核对事实，开放题逐项确认后再填写。');
}
$('plan-file').addEventListener('change',async()=>{try{loadPlan(await $('plan-file').files[0].text());}catch(e){status(e.message);}});
bind('load-plan',()=>loadPlan($('plan-text').value));
function renderAnswers(){
  $('answers').replaceChildren();$('answer-details').hidden=!answers.length;
  $('answer-title').textContent=answers.some(a=>!a.result?.ok)?'核对后填入':'本轮填写明细';$('answer-count').textContent=String(answers.length);
  for(const a of answers){
    const f=snapshot.fields.find(x=>x.id===a.field_id),wrap=show('div','','answer');
    const heading=show('div',f.label,'answer-heading');heading.append(show('span',a.result?.ok?'已填写':a.kind==='draft'?'草稿待确认':a.suggested?'请核对':'简历原文',a.result?.ok?'badge success':a.kind==='draft'?'badge draft':'badge'));wrap.append(heading);
    if(a.kind==='draft'){
      const input=document.createElement('textarea');input.value=a.value;input.readOnly=!!a.result?.ok;input.setAttribute('aria-label',f.label+'草稿');input.addEventListener('input',()=>{a.value=input.value;a.approved=false;wrap.querySelector('input[type=checkbox]').checked=false;updateAnswerAction();});wrap.append(input);
      const label=show('label','','check'),check=document.createElement('input');check.type='checkbox';check.checked=!!a.approved;check.disabled=!!a.result?.ok;check.addEventListener('change',()=>{a.approved=check.checked;updateAnswerAction();});label.append(check,document.createTextNode(a.result?.ok?'已核对并填入，后续修改请在官网完成':'我已核对这段草稿'));wrap.append(label);
    } else wrap.append(show('p',a.value));
    if(a.result)wrap.append(show('p',a.result.reason,'answer-result'));
    $('answers').append(wrap);
  }
  updateAnswerAction();updateControls();
}
bind('fill-plan',async()=>{
  if(!snapshot)throw Error('先识别页面。');
  const selected=answers.filter(a=>!a.result?.ok&&(a.kind==='fact'||a.approved));
  if(!selected.length)throw Error('请至少确认一个草稿。');
  // Revalidate fact provenance after any UI edits; drafts remain user-reviewed.
  validatePlan({schema_version:'1',kind:'junshi-fill-plan',session_id:snapshot.session_id,resume_sha256:profile.sha256,answers:selected},snapshot,profile);
  const result=await message('fill',{session_id:snapshot.session_id,answers:selected.map(({field_id,value})=>({field_id,value}))});
  for(const r of result){const a=answers.find(x=>x.field_id===r.id);if(a)a.result=r;}reflectFill(result);renderAnswers();reportFill(result,{plan:true});
});
async function record(statusValue){
  await refreshRecordPage();
  if(pendingRecordPage)throw Error('网页已变化，请先选择这次记录属于哪个岗位，尚未保存。');
  const url=safeUrl(recordPage.url),old=records.find(r=>r.url===url);
  const usedProfile=needsProfileRefresh(profile)||(statusValue==='submitted'&&!$('used-resume').checked)?null:profile;
  const updated=makeRecord(old,{page:recordPage},usedProfile,{company:$('company').value,role:$('role').value,status:statusValue,note:$('note').value});
  if(old)records[records.indexOf(old)]=updated;else records.unshift(updated);
  await save();renderRecords();$('record-editor').open=false;$('used-resume').checked=false;
  status(statusValue==='submitted'?'已记下你的实际投递确认；未把记录时间当作提交时间。':updated.events.some(e=>e.status==='submitted')?'备注已保存，原投递状态保留。':'已收藏，没有标为已投递。','success');
}
bind('save-job',()=>record('saved'));bind('submitted',()=>record('submitted'));
bind('refresh-record-source',async()=>{await refreshRecordPage();status(pendingRecordPage?'网页已变化，请选择这次记录属于哪个岗位。':'已核对当前记录来源，保存前仍会检查网页。');});
bind('record-source-keep',()=>{if(!pendingRecordPage)throw Error('没有待核对的网页变化。');recordAcknowledgedPage=pageIdentity(pendingRecordPage);pendingRecordPage=null;$('record-source-warning').hidden=true;status('仍记录原岗位；请重新核对实际使用的简历后保存。');});
bind('record-source-current',()=>{if(!pendingRecordPage)throw Error('没有待核对的网页变化。');const page=pendingRecordPage;snapshot=null;answers=[];lastFillResults=[];canUndo=false;invalidateAPI();selectRecordPage(page,{clear:true});renderAnswers();status('已改用当前网页，旧岗位资料与简历使用确认已清空。');});
const statusNames={saved:'收藏未投',submitted:'已投递',interview:'面试',rejected:'明确拒绝',offer:'Offer',withdrawn:'撤回'};
function renderRecords(){
  const search=$('search').value.trim().toLowerCase();$('records').replaceChildren();
  $('records-count').textContent=String(records.length);$('records-count').hidden=!records.length;
  $('record-overview').textContent=records.length?`${records.length} 条记录 · ${records.filter(r=>r.events.some(e=>e.status==='submitted')).length} 条本人确认已投递`:'收藏不等于投递，提交后再确认。';
  const filtered=records.filter(r=>`${r.company} ${r.role} ${r.title}`.toLowerCase().includes(search));
  if(!filtered.length){const empty=show('div','','empty-state');empty.append(show('strong',search?'没有找到匹配的记录':'还没有投递记录'),show('p',search?'试试其他公司名或岗位关键词。':'先填好手头这份申请，提交后回来确认。'));$('records').append(empty);}
  for(const r of filtered){
    const card=show('div','','record'),latest=r.events.at(-1),original=r.events.find(e=>e.status==='submitted');
    const heading=show('div','','record-heading');heading.append(show('p',r.company||'公司待补','company-name'),show('span',statusNames[latest.status],['submitted','interview','offer'].includes(latest.status)?'badge success':'badge'));
    card.append(heading,show('h3',r.role||r.title),show('p',`记录于 ${new Date(latest.at).toLocaleString('zh-CN')}\n${original?'原投简历':'关联简历'}：${(original?.resume||latest.resume).name}`,'record-meta'));
    const actions=show('div','','record-actions'),link=document.createElement('a');link.href=safeUrl(r.url);link.target='_blank';link.rel='noopener noreferrer';link.textContent='查看岗位 ↗';actions.append(link);
    const exportButton=show('button','交给军师继续','text-button');exportButton.addEventListener('click',async()=>{try{download('junshi-career-context.json',await exportSnapshot(r));status('已导出选中记录的军师兼容快照；未导出整份简历。');}catch(e){status(e.message,'error');}});actions.append(exportButton);card.append(actions);
    const progress=show('details','','disclosure');progress.append(show('summary','更新进展'));const feedback=document.createElement('input');feedback.placeholder='招聘方实际反馈，可留空';feedback.maxLength=600;feedback.setAttribute('aria-label','实际反馈');progress.append(feedback);const controls=show('div','','actions');
    const select=document.createElement('select');select.setAttribute('aria-label','更新'+(r.role||r.title)+'状态');for(const v of ['interview','rejected','offer','withdrawn']){const o=document.createElement('option');o.value=v;o.textContent=statusNames[v];select.append(o);}controls.append(select);
    const update=show('button','记录反馈','secondary');update.addEventListener('click',async()=>{update.disabled=true;try{const next=makeRecord(r,{page:{url:r.url,title:r.title}},null,{status:select.value,note:feedback.value});records[records.indexOf(r)]=next;await save();renderRecords();status('反馈已记录，原投简历版本保留。','success');}catch(e){status(e.message,'error');}finally{update.disabled=false;}});controls.append(update);progress.append(controls);card.append(progress);$('records').append(card);
  }
}
$('search').addEventListener('input',renderRecords);
bind('backup',()=>download('junshi-applications-backup.json',{schema_version:'1',kind:'junshi-applications-backup',applications:records}));
$('backup-file').addEventListener('change',async()=>{try{
  const file=$('backup-file').files[0];if(file.size>1000000)throw Error('备份超过1MB，请选择较小的备份。');
  const value=JSON.parse(await file.text());
  if(value.schema_version!=='1'||value.kind!=='junshi-applications-backup'||!Array.isArray(value.applications)||value.applications.length>1000)throw Error('不是投递记录备份。');
  const incoming=value.applications;
  for(const r of incoming){
    if(typeof r.id!=='string'||typeof r.title!=='string'||typeof r.company!=='string'||typeof r.role!=='string'||!Array.isArray(r.events)||!r.events.length||r.events.length>500)throw Error('备份记录不完整。');
    r.url=safeUrl(r.url);
    for(const e of r.events)if(!statusNames[e.status]||!Number.isFinite(Date.parse(e.at))||typeof e.resume?.name!=='string'||typeof e.note!=='string')throw Error('备份事件不完整。');
  }
  // Conflicting histories are not silently merged. The existing record wins.
  let added=0;for(const r of incoming)if(!records.some(x=>x.id===r.id||x.url===r.url)){records.push(r);added++;}
  await save();renderRecords();status(`恢复 ${added} 条，已有同ID/链接的记录保留，未覆盖。`);
}catch(e){status(e.message);}});
bind('clear-data',async()=>{if(!confirm('清除当前浏览器保存的简历、投递记录与 API 配置？请先导出备份。'))return;await chrome.storage.local.remove(['profile','records']);await removeAPI(chrome.storage);invalidateAPI();clearRecordDraft();profile=null;snapshot=null;tabId=null;recordPage=null;pendingRecordPage=null;recordAcknowledgedPage='';$('record-source-warning').hidden=true;canUndo=false;lastFillResults=[];answers=[];records=[];renderProfile();renderAnswers();renderRecords();await renderAPIState();status('已清除本地数据与密钥；浏览器站点授权和已下载备份可另行管理。');});
function invalidateAPI(){apiPrepared=null;$('api-request').hidden=true;$('api-payload').textContent='';}
function apiInputs(){return apiConfig({provider:$('api-provider').value,endpoint:$('api-endpoint').value,model:$('api-model').value,jsonMode:$('api-json').checked,rememberKey:$('api-remember').checked});}
async function renderAPIState(){
  const {config,key}=await readAPI(chrome.storage);
  if(config){$('api-provider').value=config.provider;$('api-endpoint').value=config.endpoint;$('api-model').value=config.model;$('api-json').checked=config.jsonMode;$('api-remember').checked=config.rememberKey;}
  else{$('api-provider').value='deepseek';$('api-endpoint').value=PRESETS.deepseek.endpoint;$('api-model').value=PRESETS.deepseek.model;$('api-json').checked=true;$('api-remember').checked=false;$('api-content').checked=false;$('api-advanced').open=false;}
  $('api-key').value='';$('api-key').placeholder=key?'留空沿用当前地址的已保存密钥':'只在这里填写，不要发送到聊天';
  $('api-key').type='password';$('toggle-key').textContent='显示';$('toggle-key').setAttribute('aria-pressed','false');
  apiReady=!!config&&!!key;$('api-badge').textContent=apiReady?'已配置':config?'待填写密钥':'未配置';$('api-badge').className=apiReady?'badge success':'badge';
  $('mode-badge').replaceChildren(show('i',''),document.createTextNode(apiReady?'API 已配置':'本地模式'));
  $('ai-summary').textContent=apiReady?`${config.model} · 先预览，再发送。`:'尚未连接模型；可去设置，或交给现有军师。';
  $('api-state').textContent=config?`${config.model} · ${new URL(config.endpoint).host} · ${key?(config.rememberKey?'密钥已保存在本机':'密钥只在当前浏览器会话'):'需要重新填写密钥'}`:'尚未配置。未配置也能使用本地填表和 OCR。';
  updateModelHint();updateControls();
}
$('api-provider').addEventListener('change',()=>{invalidateAPI();const preset=PRESETS[$('api-provider').value];if(preset){$('api-endpoint').value=preset.endpoint;$('api-model').value=preset.model;}else $('api-advanced').open=true;$('api-key').value='';updateModelHint();});
for(const id of ['api-endpoint','api-model','api-key','api-json','api-remember','api-content','jd'])$(id).addEventListener('input',invalidateAPI);
bind('api-save',async()=>{
  const config=apiInputs();
  // Request on the original click, before any awaited storage or network work.
  const granted=await chrome.permissions.request({origins:[permissionOrigin(config)]});
  if(!granted)throw Error('未获得 API 地址授权，本地功能仍可使用。');
  await saveAPI(chrome.storage,config,$('api-key').value);invalidateAPI();await renderAPIState();status('API 配置已保存，尚未发送任何资料；可先测试连接。');
});
bind('api-test',async()=>{
  const {config,key}=await readAPI(chrome.storage);if(!config||!key)throw Error('请先保存 API 配置和密钥。');
  if($('api-key').value.trim()||JSON.stringify(apiInputs())!==JSON.stringify(config))throw Error('设置或密钥已修改，请先保存配置。');
  status('正在发送一次合成连接测试，不含简历…');
  document.querySelector('main').inert=true;
  try{
  const r=await chrome.runtime.sendMessage({type:'api-test',data:{endpoint:config.endpoint,model:config.model}});
  if(!r?.ok)throw Error(r?.error||'接口测试没有完成。');status('合成 JSON 连接测试通过；这不代表真实表单或草稿质量已验证。');
  }finally{document.querySelector('main').inert=false;}
});
bind('api-clear',async()=>{
  const {config}=await readAPI(chrome.storage);await removeAPI(chrome.storage);invalidateAPI();await renderAPIState();
  let removed=!config;
  try{if(config)removed=await chrome.permissions.remove({origins:[permissionOrigin(config)]});}
  catch{/* Browser cannot revoke a required or inherited grant; credentials are already removed. */}
  status(removed?'API 配置、密钥和对应授权已移除。':'API 配置和密钥已移除；网站授权可在浏览器扩展设置管理。');
});
bind('api-preview',async()=>{
  if(!snapshot?.fields||!profile?.confirmed)throw Error('请先确认简历，再点击“识别并填入确定项”。');
  const {config,key}=await readAPI(chrome.storage);if(!config||!key)throw Error('请先保存 API 配置和密钥。');
  if($('api-key').value.trim()||JSON.stringify(apiInputs())!==JSON.stringify(config))throw Error('设置或密钥已修改，请先保存配置。');
  snapshot=await message('scan',{keepHistory:true});answers=[];lastFillResults=[];renderAnswers();renderFillSummary();
  const context=buildAIContext(snapshot,profile,{includeContent:$('api-content').checked,jd:$('jd').value});
  apiPrepared={context,config,session:snapshot.session_id,sha:profile.sha256};
  $('api-scope').textContent=`发往 ${config.endpoint}，模型 ${config.model}，共 ${context.fields.length} 个空白字段。${context.mode==='content'?'包含已确认简历内容与 JD，可能含联系方式。':'只含字段标签、选项、分组与资料字段类型；不含简历正文或已填值。网页标签可能夹带个人信息，请检查。'}发送后仅生成预览，不自动填写。`;
  $('api-payload').textContent=JSON.stringify(context,null,2);$('api-request').hidden=false;status('请检查发送范围，点击发送后只请求一次。');
});
bind('api-run',async()=>{
  const prepared=apiPrepared;if(!prepared||prepared.sha!==profile?.sha256||prepared.session!==snapshot?.session_id)throw Error('资料或表单已变化，请重新预览。');
  await assertFormTarget();
  document.querySelector('main').inert=true;status('正在请求模型，最多等待25秒，不自动重试…');
  try{
    const r=await chrome.runtime.sendMessage({type:'api-generate',data:{endpoint:prepared.config.endpoint,model:prepared.config.model,context:prepared.context}});
    if(!r?.ok)throw Error(r?.error||'模型请求未完成。');
    if(prepared.sha!==profile?.sha256||prepared.session!==snapshot?.session_id)throw Error('本次资料已失效，未采用模型结果。');
    answers=resolveAIPlan(r.result,prepared.context,snapshot,profile).map(a=>({...a,suggested:true}));renderAnswers();revealAnswers();
    status(`得到 ${answers.length} 项待核对方案。事实值取自简历，开放题仍需逐项勾选；尚未填写。`);
  }finally{invalidateAPI();document.querySelector('main').inert=false;}
});
function updateAnswerAction(){
  const pending=answers.filter(a=>!a.result?.ok),selected=pending.filter(a=>a.kind==='fact'||a.approved);
  $('fill-plan').hidden=!pending.length;$('fill-plan').disabled=!selected.length;
  $('fill-plan').textContent=selected.length?`填入已确认的方案（${selected.length} 项）`:'先勾选已核对的草稿';
}
function updateControls(){
  $('resume-card').classList.toggle('has-profile',!!profile);
  const legacy=needsProfileRefresh(profile);
  $('resume-badge').textContent=legacy?'需重新导入':profile?(profile.confirmed?'已确认':'待确认'):'未导入';$('resume-badge').className=legacy?'badge draft':profile?.confirmed?'badge success':'badge';
  $('import-label').textContent=profile?'更换简历':'选择本次简历';$('upload-formats').textContent=profile?'选择本次准备投递的版本':'PDF、图片、文字或军师 JSON';
  $('confirm-resume').hidden=!profile||profile.confirmed||legacy;$('confirm-resume').disabled=legacy;
  $('profile-refresh-note').hidden=!legacy;$('resume-text').readOnly=legacy;$('reparse').disabled=legacy;
  $('scan').disabled=!profile?.confirmed;$('undo').disabled=!canUndo;
  $('scan-hint').textContent=profile?.confirmed?'准备好了。点击上方按钮，填写官网当前页。':'先导入并确认简历，即可开始填写。';
  if(legacy)$('scan-hint').textContent='解析更新后，请重新导入本次附件；投递历史不受影响。';
  const hasPage=Array.isArray(snapshot?.fields);$('assistance').hidden=!hasPage;$('continue-record').hidden=!hasPage;
  $('api-preview').disabled=!profile?.confirmed||!hasPage||!apiReady;
  $('record-page').textContent=recordPage?`${recordPage.title}\n${new URL(recordPage.url).host}`:'请先读取当前招聘网页';
  $('used-resume').disabled=!profile||legacy;$('used-resume-name').textContent=legacy?'旧简历需重新导入后才能关联本次投递。':profile?`${profile.file_name||profile.name}；不确定可不选，原投版本保持未知。`:'尚未导入。未选择时，原投版本保持未知。';
  $('save-job').disabled=!!pendingRecordPage;$('submitted').disabled=!!pendingRecordPage;
  $('page-title').textContent=snapshot?.page?.title||'打开招聘官网的申请表单';
  renderFillSummary();
  updateAnswerAction();
  for(const button of document.querySelectorAll('button[aria-busy=true]'))button.disabled=true;
}
function reflectFill(result){
  lastFillResults.push(...result);canUndo=canUndo||result.some(r=>r.ok);
  for(const r of result)if(r.ok){const f=snapshot.fields.find(f=>f.id===r.id);if(f)f.filled=true;}
  renderFillSummary();
}
function reportFill(result,{plan=false}={}){
  const filled=result.filter(r=>r.ok).length,failed=result.length-filled;
  $('answer-details').open=failed>0||plan;
  if(failed){status(`已填 ${filled} 项，另有 ${failed} 项未完成；展开的明细说明了原因。`,filled?'info':'error');return;}
  if(!filled){status('本轮没有可自动填写的空白项。请检查官网，或补充资料后重试。');return;}
  status(`${plan?'本轮已填':'已填'} ${filled} 项。请检查官网；剩余空项可在下方补全。`,'success');
}
function renderFillSummary(){
  const fields=snapshot?.fields;$('field-summary').hidden=!fields;
  if(!fields){$('field-summary').replaceChildren();return;}
  const written=new Set(lastFillResults.filter(r=>r.ok).map(r=>r.id)),supported=fields.filter(f=>f.supported);
  const values=[[written.size,'本轮填入'],[supported.filter(f=>f.filled&&!written.has(f.id)).length,'原有保留'],[supported.filter(f=>!f.filled).length,'待补充']];
  $('field-summary').replaceChildren(...values.map(([n,label])=>{const e=show('div','','metric');e.append(show('strong',String(n)),show('span',label));return e;}));
  $('scan-hint').textContent=`${fields.filter(f=>!f.supported).length} 项需在官网手动处理。${snapshot.limits?.iframes?'含 iframe，框内字段另行检查。':''}`;
}
function revealAnswers(){
  $('answer-details').open=true;$('assistance').open=false;
  requestAnimationFrame(()=>{if(!$('panel-fill').hidden)$('answer-details').scrollIntoView({block:'nearest'});});
}
function updateModelHint(){$('api-model-hint').textContent=$('api-model').value+($('api-provider').value==='custom'?' · 自定义接口':' · 接口与模型可在高级选项修改');}
function activatePanel(name){
  if(!['fill','records','settings'].includes(name))return;
  for(const tab of document.querySelectorAll('[role=tab]')){const selected=tab.dataset.openPanel===name;tab.setAttribute('aria-selected',String(selected));tab.tabIndex=selected?0:-1;$('panel-'+tab.dataset.openPanel).hidden=!selected;}
  document.querySelector('main').scrollTop=0;
  if(name==='records'&&recordPage)refreshRecordPage().catch(e=>status(e.message,'error'));
}
for(const button of document.querySelectorAll('[data-open-panel]'))button.addEventListener('click',()=>activatePanel(button.dataset.openPanel));
document.querySelector('[role=tablist]').addEventListener('keydown',event=>{
  const tabs=[...document.querySelectorAll('[role=tab]')],index=tabs.indexOf(document.activeElement);if(index<0)return;
  const next={ArrowRight:(index+1)%tabs.length,ArrowLeft:(index+tabs.length-1)%tabs.length,Home:0,End:tabs.length-1}[event.key];
  if(next===undefined)return;event.preventDefault();activatePanel(tabs[next].dataset.openPanel);tabs[next].focus();
});
$('continue-record').addEventListener('click',()=>{$('record-editor').open=true;$('company').focus();});
$('toggle-key').addEventListener('click',()=>{const visible=$('api-key').type==='password';$('api-key').type=visible?'text':'password';$('toggle-key').textContent=visible?'隐藏':'显示';$('toggle-key').setAttribute('aria-pressed',String(visible));});
$('api-model').addEventListener('input',updateModelHint);
$('app-version').textContent='v'+chrome.runtime.getManifest().version;
renderProfile();renderRecords();await renderAPIState();renderFillSummary();document.querySelector('main').inert=false;
