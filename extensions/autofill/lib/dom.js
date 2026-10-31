// Native setter/event pattern adapted from wangshen-autofill (MIT).
// Full upstream notice is included in licenses/wangshen-autofill.txt.
(() => {
  if(globalThis.JunshiDOM)return;
  const nodes=new Map(), history=[];
  let session='',href='',seq=0;
  const sensitive=s=>/密码|口令|验证码|身份证|护照|银行卡|信用卡|签证|工作许可|工作资格|薪资|薪酬|期望工资|政治面貌|民族|婚姻|出生|国籍|最高学历|password|passcode|otp|passport|social.security|bank|credit.card|visa|sponsor|work.?authori|salary|compensation|citizenship|nationality|ethnicity|marital|date.?of.?birth|highest.?degree/i.test(s);
  const visible=e=>!!e.getClientRects().length && getComputedStyle(e).visibility!=='hidden' && getComputedStyle(e).display!=='none';
  const val=e=>e.isContentEditable?e.textContent:e.value;
  const protectedField=e=>sensitive([label(e),e.name,e.id,e.autocomplete,e.getAttribute('placeholder')].join(' '));
  const label=e=>{
    const root=e.getRootNode(),refs=(e.getAttribute('aria-labelledby')||'').split(/\s+/).filter(Boolean);
    const aria=refs.map(id=>root.getElementById?.(id)?.textContent||'').join(' ').trim();
    return aria||e.getAttribute('aria-label')||[...(e.labels||[])].map(x=>x.textContent).join(' ').trim()||e.getAttribute('placeholder')||e.name||e.id||'未命名字段';
  };
  const fingerprint=e=>JSON.stringify([e.tagName,e.type,e.name,e.id,label(e),e.maxLength,e.autocomplete,e.getAttribute('placeholder'),e.getAttribute('role')]);
  function setValue(e,v){
    const proto=e.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:e.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;
    e.dispatchEvent(new Event('focus',{bubbles:true}));
    Object.getOwnPropertyDescriptor(proto,'value').set.call(e,v);
    for(const type of ['input','change','blur'])e.dispatchEvent(new Event(type,{bubbles:true}));
  }
  function collect(root){
    const found=[...root.querySelectorAll('input,textarea,select,[role="combobox"],[contenteditable="true"]')];
    for(const e of root.querySelectorAll('*'))if(e.shadowRoot)found.push(...collect(e.shadowRoot));
    return [...new Set(found)];
  }
  function scan({keepHistory=false}={}){
    session=crypto.randomUUID();href=location.href;nodes.clear();if(!keepHistory)history.length=0;seq=0;
    const groups=new Map(), counters={education:0,project:0,work:0};
    const fields=[];
    for(const e of collect(document)){
      if(!visible(e)||e.disabled||e.readOnly||['hidden','submit','button','reset','image'].includes(e.type))continue;
      const id='f'+(++seq), text=label(e).replace(/\s+/g,' ').trim().slice(0,240);
      const container=e.closest('fieldset,[data-junshi-group],section');
      const heading=container?.querySelector('legend,h2,h3,h4,[data-group-title]')?.textContent||'';
      const group=/教育|学历|education/i.test(heading)?'education':/项目|project/i.test(heading)?'project':/工作|实习|work|employment/i.test(heading)?'work':'';
      let index=0;if(group){if(!groups.has(container))groups.set(container,counters[group]++);index=groups.get(container);}
      const isBlocked=protectedField(e)||['password','checkbox','radio','file','color','range'].includes(e.type);
      const supported=['INPUT','TEXTAREA','SELECT'].includes(e.tagName)&&e.getAttribute('role')!=='combobox'&&!isBlocked;
      nodes.set(id,{el:e,fp:fingerprint(e)});
      fields.push({id,label:text,name:e.name||'',placeholder:e.getAttribute('placeholder')||'',autocomplete:e.autocomplete||'',type:e.tagName==='SELECT'?'select':e.type||'text',group,group_index:index,filled:!!String(val(e)||'').trim(),blocked:isBlocked,supported,
        options:e.tagName==='SELECT'?[...e.options].filter(o=>!o.disabled).map(o=>({value:o.value,text:o.textContent.trim()})).slice(0,100):[],max_length:e.maxLength>0?e.maxLength:null});
      if(fields.length>=150)break;
    }
    return {session_id:session,page:{url:href,title:document.title.slice(0,200)},fields,limits:{iframes:document.querySelectorAll('iframe').length,scope:'main document and open shadow roots; custom pickers/manual upload require review'}};
  }
  async function apply(request){
    if(request.session_id!==session||location.href!==href)throw Error('页面已经变化，请重新识别。');
    const result=[];
    for(const a of request.answers){
      const entry=nodes.get(a.field_id),e=entry?.el;
      let reason='';
      if(!e?.isConnected||!visible(e)||e.disabled||e.readOnly||fingerprint(e)!==entry.fp)reason='字段已变化';
      else if(protectedField(e)||!['INPUT','TEXTAREA','SELECT'].includes(e.tagName)||['password','checkbox','radio','file','hidden','submit','button','reset','image','range','color'].includes(e.type)||e.getAttribute('role')==='combobox')reason='需要手动填写';
      else if(String(val(e)||'').trim())reason='保留已有内容';
      else if(typeof a.value!=='string'||!a.value.trim())reason='没有有效值';
      else if(e.maxLength>0&&a.value.length>e.maxLength)reason='超出字数限制，未截断';
      if(reason){result.push({id:a.field_id,ok:false,reason});continue;}
      let target=a.value;
      if(e.tagName==='SELECT'){
        const norm=s=>s.normalize('NFKC').toLowerCase().replace(/\s/g,'');
        const options=[...e.options].filter(o=>!o.disabled&&o.value&&(norm(o.textContent)===norm(target)||norm(o.value)===norm(target)));
        if(options.length!==1){result.push({id:a.field_id,ok:false,reason:'下拉选项没有唯一精确匹配'});continue;}
        target=options[0].value;
      }
      if(e.type==='date'&&!/^\d{4}-\d{2}-\d{2}$/.test(target)){result.push({id:a.field_id,ok:false,reason:'日期缺少精度，未补造日'});continue;}
      if(e.type==='month'&&!/^\d{4}-\d{2}$/.test(target)){result.push({id:a.field_id,ok:false,reason:'月份格式需确认'});continue;}
      const before=val(e);setValue(e,target);
      await new Promise(r=>setTimeout(r,40));
      const ok=val(e)===target;
      if(ok){history.push({el:e,before,after:target});e.style.outline='2px solid #4a8874';}
      result.push({id:a.field_id,ok,reason:ok?'已填写':'网页未保留值，请手动检查'});
    }
    return result;
  }
  function undo(){let restored=0;for(const r of history.splice(0).reverse()){if(r.el.isConnected&&val(r.el)===r.after){setValue(r.el,r.before);r.el.style.outline='';restored++;}}return {restored};}
  globalThis.JunshiDOM={scan,apply,undo};
})();
