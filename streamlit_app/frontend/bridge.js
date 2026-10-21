/* Session-only Streamlit transport. Every read remains authorized on the server. */
const pending=new Map(),queue=[],reads=new Map();
const release=document.currentScript?.dataset.release||'';
let current=null,loaded=false,lastActor=null,scheduled=false,lastHeight=0,heightFrame=0;
function send(type,extra={}){window.parent.postMessage({isStreamlitMessage:true,type,...extra},'*');}
function height(){if(heightFrame)return;heightFrame=requestAnimationFrame(()=>{heightFrame=0;const next=Math.max(800,Math.ceil(document.body.getBoundingClientRect().height));if(next!==lastHeight){lastHeight=next;send('streamlit:setFrameHeight',{height:next});}});}
function pump(){
 scheduled=false;if(current||!queue.length)return;
 const first=queue.shift(),group=[first];
 // Adjacent reads share one rerun and one PHP/DB connection. A write is a barrier.
 if(first.method==='GET')while(queue[0]?.method==='GET'&&group.length<16)group.push(queue.shift());
 current=group.length===1?first:{id:crypto.randomUUID(),path:'__batch',method:'GET',active_site:first.active_site,requests:group};
 send('streamlit:setComponentValue',{value:current,dataType:'json'});
}
function schedule(){if(!scheduled){scheduled=true;setTimeout(pump,0);}}
window.hseBridge=function(path,{method='GET',data,form}={}){
 const active_site=new URL(location.href).searchParams.get('hse_site');
 const key=method==='GET'&&!data&&!form?active_site+'|'+path:null;
 if(key&&reads.has(key))return reads.get(key);
 if(method!=='GET')reads.clear();
 const promise=(async()=>{
  const request={id:crypto.randomUUID(),path,method,data:data||null,form:{},files:{},active_site};
  if(form)for(const [key,value]of form.entries()){
   if(value instanceof File){
    if(value.size>15*1024*1024)throw new Error('Limite file: 15 MB');
    const bytes=new Uint8Array(await value.arrayBuffer());let binary='';
    for(let i=0;i<bytes.length;i+=32768)binary+=String.fromCharCode(...bytes.subarray(i,i+32768));
    request.files[key]={name:value.name,base64:btoa(binary)};
   }else request.form[key]=value;
  }
  return new Promise((resolve,reject)=>{pending.set(request.id,{resolve,reject});queue.push(request);schedule();});
 })();
 if(key){reads.set(key,promise);const clear=()=>{if(reads.get(key)===promise)reads.delete(key);};promise.then(clear,clear);}
 return promise;
};
function settle(response){
 const p=pending.get(response.id);if(!p)return;pending.delete(response.id);
 if(response.error){const e=new Error(response.error.message);e.field=response.error.details?.field;e.current=response.error.status===409?response.error.details:null;p.reject(e);}else p.resolve(response.data);
}
window.addEventListener('message',event=>{
 if(event.source!==window.parent||event.data?.type!=='streamlit:render')return;
 const args=event.data.args;if(!args?.config)return;
 if(lastActor!==null&&lastActor!==args.config.user){location.reload();return;}lastActor=args.config.user;
 if(!loaded){
  loaded=true;
  if(args.config.selected_site){const url=new URL(location.href);url.searchParams.set('hse_site',args.config.selected_site);history.replaceState(null,'',url);}
  window.HSE_CONFIG={...args.config,api:'streamlit://bridge',assets:new URL('assets/',location.href).href};
  const script=document.createElement('script');script.type='module';script.src='assets/app.bundle.js'+(release?'?v='+encodeURIComponent(release):'');
  script.onerror=()=>{const status=document.querySelector('#hse-platform');status.textContent='Caricamento non riuscito. Ricarica la pagina per riprovare.';status.setAttribute('role','alert');};
  document.body.append(script);new ResizeObserver(height).observe(document.body);
 }
 for(const response of args.responses||[]){
  if(current?.id===response.id){
   if(current.requests){
    if(response.error)for(const r of current.requests)settle({id:r.id,error:response.error});
    else for(const item of response.data||[])settle(item);
   }else settle(response);
   current=null;schedule();
  }
 }
 height();
});
send('streamlit:componentReady',{apiVersion:1});height();
