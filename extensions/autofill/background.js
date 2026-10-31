import {readAPI} from './lib/api-settings.mjs';
import {permissionOrigin,requestCompletion} from './lib/api.mjs';
let apiBusy=false;

chrome.runtime.onInstalled.addListener(async()=>{
  await chrome.storage.local.setAccessLevel({accessLevel:'TRUSTED_CONTEXTS'});
  await chrome.sidePanel.setPanelBehavior({openPanelOnActionClick:true});
});
chrome.runtime.onMessage.addListener((message,sender,sendResponse)=>{
  // Only our extension pages can request injection. No externally_connectable API.
  if(sender.id!==chrome.runtime.id||!sender.url?.startsWith(chrome.runtime.getURL('')))return;
  if(!['scan','fill','undo','api-test','api-generate'].includes(message.type))return;
  (async()=>{
    if(message.type.startsWith('api-')){
      if(apiBusy)throw Error('已有模型请求进行中，请等待完成后再试。');
      apiBusy=true;
      try{
      const {config,key}=await readAPI(chrome.storage);
      if(!config||!key)throw Error('请先配置 API 和密钥；浏览器重启后，会话密钥需要重新填写。');
      if(message.data?.endpoint!==config.endpoint||message.data?.model!==config.model)throw Error('API 配置已变化，请重新预览。');
      if(!await chrome.permissions.contains({origins:[permissionOrigin(config)]}))throw Error('API 站点授权已撤回，请重新保存配置并授权。');
      const test=message.type==='api-test',context=message.data?.context;
      if(!test&&(!['mapping','content'].includes(context?.mode)||context.kind!=='junshi-api-context'||JSON.stringify(context).length>180000))throw Error('请先预览本次发送范围。');
      const result=await requestCompletion(config,key,context,{test});
      sendResponse({ok:true,result});return;
      }finally{apiBusy=false;}
    }
    const tab=await chrome.tabs.get(message.tabId);
    if(!/^https?:\/\//.test(tab.url||''))throw Error('请在招聘官网点击扩展图标后再识别。');
    await chrome.scripting.executeScript({target:{tabId:tab.id},files:['lib/dom.js']});
    const [r]=await chrome.scripting.executeScript({target:{tabId:tab.id},func:async(type,data)=>{
      if(type==='scan')return JunshiDOM.scan(data||{});
      if(type==='fill')return JunshiDOM.apply(data);
      return JunshiDOM.undo();
    },args:[message.type,message.data||null]});
    sendResponse({ok:true,result:r.result});
  })().catch(e=>sendResponse({ok:false,error:e.message}));
  return true;
});
