import {makeProfile,localPlan,validatePlan,makeHandoff,makeRecord,exportSnapshot,safeUrl,sha256} from './lib/core.mjs';
import {readResume} from './lib/read-resume.mjs';
import {PRESETS,apiConfig,permissionOrigin,buildAIContext,resolveAIPlan} from './lib/api.mjs';
import {readAPI,saveAPI,removeAPI} from './lib/api-settings.mjs';
const $=id=>document.getElementById(id);
let profile=null,snapshot=null,tabId=null,answers=[],records=[];
let apiPrepared=null;
const status=s=>{$('status').textContent=s;};
const show=(tag,text,cls='')=>{const e=document.createElement(tag);e.textContent=text;e.className=cls;return e;};
// Resolve persisted state before registering an import/save action. An import may
// never race a late initial read and be replaced by an old profile or null.
try{const state=await chrome.storage.local.get(['profile','records']);profile=state.profile||null;records=state.records||[];}
catch(e){status(e.message);}
async function save(){await chrome.storage.local.set({profile,records});}
function bind(id,fn){$(id).addEventListener('click',async()=>{const b=$(id);b.disabled=true;try{await fn();}catch(e){status(e.message);}finally{b.disabled=false;}});}
async function message(type,data){const r=await chrome.runtime.sendMessage({type,tabId,data});if(!r?.ok)throw Error(r?.error||'无法操作当前表单，请回到网页重新点击扩展。');return r.result;}
function download(name,value){const blob=new Blob([typeof value==='string'?value:JSON.stringify(value,null,2)],{type:name.endsWith('.json')?'application/json':'text/plain;charset=utf-8'});const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),30000);}
function renderProfile(){
  $('resume-meta').textContent=profile?`${profile.name} · ${profile.confirmed?'已确认':'待你检查确认'}${profile.ocr?' · OCR识别结果':''}`:'尚未导入简历';
  $('resume-text').value=profile?.text||'';
  $('facts').replaceChildren(...(profile?.facts||[]).filter(f=>f.key!=='source').map(f=>show('p',`${f.key}${f.group?` / ${f.group} ${f.index+1}`:''}：${f.value}`)));
}
$('resume-file').addEventListener('change',async()=>{invalidateAPI();document.querySelector('main').inert=true;try{status('正在读取…');profile=await readResume($('resume-file').files[0],{ocr:$('use-ocr').checked,progress:status});snapshot=null;answers=[];renderAnswers();renderProfile();status('已本地识别，请展开检查文字，然后确认。');}catch(e){status(e.message);}finally{document.querySelector('main').inert=false;}});
$('resume-text').addEventListener('input',()=>{if(!profile)return;profile.confirmed=false;invalidateAPI();answers=[];renderAnswers();$('resume-meta').textContent=profile.name+' · 文字已修改，请更新并重新确认';});
bind('reparse',async()=>{invalidateAPI();if(!profile)throw Error('请先导入简历。');const text=$('resume-text').value,old=profile;profile=makeProfile(text,{name:old.name+'（文字修订）',sha:await sha256(text),ocr:old.ocr});profile.file_name=old.file_name||old.name;profile.file_sha256=old.file_sha256||old.sha256;snapshot=null;answers=[];renderAnswers();renderProfile();status('已更新填表文字，旧方案已失效；原附件文件指纹保留，请确认资料。');});
bind('confirm-resume',async()=>{if(!profile)throw Error('请先导入简历。');if($('resume-text').value!==profile.text)throw Error('识别文字已修改，请先点击“按修改后的文字更新”。');profile.confirmed=true;await save();renderProfile();status('这份简历已确认并保存在当前浏览器本机。');});
bind('scan',async()=>{
  invalidateAPI();
  if(!profile?.confirmed)throw Error('请先确认本次简历。');
  const [tab]=await chrome.tabs.query({active:true,currentWindow:true});tabId=tab.id;
  snapshot=await message('scan');answers=[];renderAnswers();
  $('page-title').textContent=snapshot.page.title;
  $('field-summary').textContent=`识别到 ${snapshot.fields.length} 项；已有内容 ${snapshot.fields.filter(f=>f.filled).length} 项；需要手动处理 ${snapshot.fields.filter(f=>!f.supported).length} 项。${snapshot.limits.iframes?'页面含iframe，框内字段需另行检查。':''}`;
  const plan=localPlan(snapshot,profile);answers=validatePlan(plan,snapshot,profile);renderAnswers();
  const result=await message('fill',{session_id:snapshot.session_id,answers});
  for(const r of result){const a=answers.find(x=>x.field_id===r.id);if(a)a.result=r;}
  renderAnswers();status(`已填 ${result.filter(r=>r.ok).length} 项。请检查；未匹配项可导出给军师，未点击任何提交。`);
});
bind('undo',async()=>{const result=await message('undo');status(`已撤销 ${result.restored} 项；你手动改过的内容保留。`);});
bind('export-context',async()=>{if(!snapshot||!profile?.confirmed)throw Error('先识别当前页并确认简历。');download('junshi-form-context.json',makeHandoff(snapshot,profile,$('jd').value));status('已导出当前表单和必要简历来源。把文件交给现有军师，生成junshi-fill-plan再导入。');});
function loadPlan(raw){
  invalidateAPI();
  if(!snapshot)throw Error('请先识别当前表单。');
  if(raw.length>500000)throw Error('方案文件过大。');
  const parsed=JSON.parse(raw.trim().replace(/^```(?:json)?\s*/,'').replace(/\s*```$/,''));
  answers=validatePlan(parsed,snapshot,profile);renderAnswers();status('方案已检查。事实有来源，开放题请逐项阅读、修改并确认后再填写。');
}
$('plan-file').addEventListener('change',async()=>{try{loadPlan(await $('plan-file').files[0].text());}catch(e){status(e.message);}});
bind('load-plan',()=>loadPlan($('plan-text').value));
function renderAnswers(){
  $('answers').replaceChildren();$('fill-plan').hidden=!answers.length;
  for(const [index,a]of answers.entries()){
    const f=snapshot.fields.find(x=>x.id===a.field_id),wrap=show('div','','answer');
    const heading=show('label',f.label);heading.append(show('span',a.kind==='draft'?'草稿·待确认':a.suggested?'模型匹配·请核对':'简历原文',a.kind==='draft'?'badge draft':'badge'));wrap.append(heading);
    if(a.kind==='draft'){
      const input=document.createElement('textarea');input.value=a.value;input.setAttribute('aria-label',f.label+'草稿');input.addEventListener('input',()=>{a.value=input.value;a.approved=false;wrap.querySelector('input[type=checkbox]').checked=false;});wrap.append(input);
      const label=show('label',''),check=document.createElement('input');check.type='checkbox';check.checked=!!a.approved;check.addEventListener('change',()=>a.approved=check.checked);label.append(check,document.createTextNode(' 我已核对这段草稿'));wrap.append(label);
    } else wrap.append(show('p',a.value));
    if(a.result)wrap.append(show('p',a.result.reason));
    $('answers').append(wrap);
  }
}
bind('fill-plan',async()=>{
  if(!snapshot)throw Error('先识别页面。');
  const selected=answers.filter(a=>a.kind==='fact'||a.approved);
  if(!selected.length)throw Error('请至少确认一个草稿。');
  // Revalidate fact provenance after any UI edits; drafts remain user-reviewed.
  validatePlan({schema_version:'1',kind:'junshi-fill-plan',session_id:snapshot.session_id,resume_sha256:profile.sha256,answers:selected},snapshot,profile);
  const result=await message('fill',{session_id:snapshot.session_id,answers:selected.map(({field_id,value})=>({field_id,value}))});
  for(const r of result){const a=answers.find(x=>x.field_id===r.id);if(a)a.result=r;}renderAnswers();status(`本轮已填 ${result.filter(x=>x.ok).length} 项；跳过已有值或已变化字段，提交仍由你完成。`);
});
async function record(statusValue){
  if(!snapshot){const [tab]=await chrome.tabs.query({active:true,currentWindow:true});snapshot={page:{url:safeUrl(tab.url),title:tab.title||''}};}
  const url=safeUrl(snapshot.page.url),old=records.find(r=>r.url===url);
  const usedProfile=statusValue==='submitted'&&!$('used-resume').checked?null:profile;
  const updated=makeRecord(old,snapshot,usedProfile,{company:$('company').value,role:$('role').value,status:statusValue,note:$('note').value});
  if(old)records[records.indexOf(old)]=updated;else records.unshift(updated);
  await save();renderRecords();status(statusValue==='submitted'?'已记下你的实际投递确认；未把记录时间当作提交时间。':'已收藏，没有标为已投递。');
}
bind('save-job',()=>record('saved'));bind('submitted',()=>record('submitted'));
const statusNames={saved:'收藏未投',submitted:'已投递',interview:'面试',rejected:'明确拒绝',offer:'Offer',withdrawn:'撤回'};
function renderRecords(){
  const search=$('search').value.trim().toLowerCase();$('records').replaceChildren();
  for(const r of records.filter(r=>`${r.company} ${r.role} ${r.title}`.toLowerCase().includes(search))){
    const card=show('div','','record'),latest=r.events.at(-1);card.append(show('h3',`${r.company||'公司待补'} · ${r.role||r.title}`),show('p',`${statusNames[latest.status]} · 记录于 ${new Date(latest.at).toLocaleString('zh-CN')} · 简历 ${latest.resume.name}`,'muted'));
    const actions=show('div','','actions'),exportButton=show('button','交给军师继续','secondary');exportButton.addEventListener('click',async()=>{try{download('junshi-career-context.json',await exportSnapshot(r));status('已导出选中记录的军师兼容快照；未导出整份简历。');}catch(e){status(e.message);}});actions.append(exportButton);
    const select=document.createElement('select');select.setAttribute('aria-label','更新'+(r.role||r.title)+'状态');for(const v of ['interview','rejected','offer','withdrawn']){const o=document.createElement('option');o.value=v;o.textContent=statusNames[v];select.append(o);}actions.append(select);
    const update=show('button','记录反馈','secondary');update.addEventListener('click',async()=>{try{const note=prompt('招聘方实际反馈（不确定可以留空）','');if(note===null)return;const next=makeRecord(r,{page:{url:r.url,title:r.title}},null,{status:select.value,note});records[records.indexOf(r)]=next;await save();renderRecords();status('反馈已记录，原投简历版本保留。');}catch(e){status(e.message);}});actions.append(update);card.append(actions);$('records').append(card);
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
bind('clear-data',async()=>{if(!confirm('清除当前浏览器保存的简历、投递记录与 API 配置？请先导出备份。'))return;await chrome.storage.local.remove(['profile','records']);await removeAPI(chrome.storage);invalidateAPI();profile=null;snapshot=null;answers=[];records=[];renderProfile();renderAnswers();renderRecords();await renderAPIState();status('已清除本地数据与密钥；浏览器站点授权和已下载备份可另行管理。');});
function invalidateAPI(){apiPrepared=null;$('api-request').hidden=true;$('api-payload').textContent='';}
function apiInputs(){return apiConfig({provider:$('api-provider').value,endpoint:$('api-endpoint').value,model:$('api-model').value,jsonMode:$('api-json').checked,rememberKey:$('api-remember').checked});}
async function renderAPIState(){
  const {config,key}=await readAPI(chrome.storage);
  if(config){$('api-provider').value=config.provider;$('api-endpoint').value=config.endpoint;$('api-model').value=config.model;$('api-json').checked=config.jsonMode;$('api-remember').checked=config.rememberKey;}
  $('api-key').value='';$('api-key').placeholder=key?'留空沿用当前地址的已保存密钥':'只在这里填写，不要发送到聊天';
  $('api-state').textContent=config?`${config.model} · ${new URL(config.endpoint).host} · ${key?(config.rememberKey?'密钥已保存在本机':'密钥只在当前浏览器会话'):'需要重新填写密钥'}`:'尚未配置。未配置也能使用本地填表和 OCR。';
}
$('api-provider').addEventListener('change',()=>{invalidateAPI();const preset=PRESETS[$('api-provider').value];if(preset){$('api-endpoint').value=preset.endpoint;$('api-model').value=preset.model;}$('api-key').value='';});
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
  const removed=config?await chrome.permissions.remove({origins:[permissionOrigin(config)]}):true;
  status(removed?'API 配置、密钥和对应授权已移除。':'API 配置和密钥已移除；网站授权可在浏览器扩展设置管理。');
});
bind('api-preview',async()=>{
  if(!snapshot?.fields||!profile?.confirmed)throw Error('请先确认简历，再点击“识别并填入确定项”。');
  const {config,key}=await readAPI(chrome.storage);if(!config||!key)throw Error('请先保存 API 配置和密钥。');
  if($('api-key').value.trim()||JSON.stringify(apiInputs())!==JSON.stringify(config))throw Error('设置或密钥已修改，请先保存配置。');
  snapshot=await message('scan',{keepHistory:true});answers=[];renderAnswers();
  const context=buildAIContext(snapshot,profile,{includeContent:$('api-content').checked,jd:$('jd').value});
  apiPrepared={context,config,session:snapshot.session_id,sha:profile.sha256};
  $('api-scope').textContent=`发往 ${config.endpoint}，模型 ${config.model}，共 ${context.fields.length} 个空白字段。${context.mode==='content'?'包含已确认简历内容与 JD，可能含联系方式。':'只含字段标签、选项、分组与资料字段类型；不含简历正文或已填值。网页标签可能夹带个人信息，请检查。'}发送后仅生成预览，不自动填写。`;
  $('api-payload').textContent=JSON.stringify(context,null,2);$('api-request').hidden=false;status('请检查发送范围，点击发送后只请求一次。');
});
bind('api-run',async()=>{
  const prepared=apiPrepared;if(!prepared||prepared.sha!==profile?.sha256||prepared.session!==snapshot?.session_id)throw Error('资料或表单已变化，请重新预览。');
  document.querySelector('main').inert=true;status('正在请求模型，最多等待25秒，不自动重试…');
  try{
    const r=await chrome.runtime.sendMessage({type:'api-generate',data:{endpoint:prepared.config.endpoint,model:prepared.config.model,context:prepared.context}});
    if(!r?.ok)throw Error(r?.error||'模型请求未完成。');
    if(prepared.sha!==profile?.sha256||prepared.session!==snapshot?.session_id)throw Error('本次资料已失效，未采用模型结果。');
    answers=resolveAIPlan(r.result,prepared.context,snapshot,profile).map(a=>({...a,suggested:true}));renderAnswers();
    status(`得到 ${answers.length} 项待核对方案。事实值取自简历，开放题仍需逐项勾选；尚未填写。`);
  }finally{invalidateAPI();document.querySelector('main').inert=false;}
});
renderProfile();renderRecords();await renderAPIState();document.querySelector('main').inert=false;
