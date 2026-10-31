import {apiConfig} from './api.mjs';

export async function readAPI(storage){
  const local=await storage.local.get(['apiConfig','apiSecret']),session=await storage.session.get('apiSecret');
  const config=local.apiConfig?apiConfig(local.apiConfig):null;
  const secret=config?.rememberKey?local.apiSecret:session.apiSecret;
  const key=config&&secret?.endpoint===config.endpoint?secret.key:'';
  return {config,key:key||''};
}
export async function saveAPI(storage,input,key){
  const config=apiConfig(input),old=await readAPI(storage);
  key=String(key||'').trim().replace(/^Bearer\s+/i,'');
  if(!key&&old.config?.endpoint===config.endpoint)key=old.key;
  if(!key||key.length>2048||/[^\x21-\x7e]/.test(key))throw Error('请在插件中填写有效 API Key，不要在聊天中发送。');
  const secret={endpoint:config.endpoint,key};
  // Write the new store before removing the old one; no key enters backups/sync.
  if(config.rememberKey)await storage.local.set({apiSecret:secret});
  else await storage.session.set({apiSecret:secret});
  await storage.local.set({apiConfig:config});
  if(config.rememberKey)await storage.session.remove('apiSecret');else await storage.local.remove('apiSecret');
  return config;
}
export async function removeAPI(storage){await storage.local.remove(['apiConfig','apiSecret']);await storage.session.remove('apiSecret');}
