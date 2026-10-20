/* Streamlit component protocol: no public API, tokens or database credentials in the browser. */
const pending=new Map(),queue=[];let current=null,loaded=false,lastActor=null;
function send(type,extra={}){window.parent.postMessage({isStreamlitMessage:true,type,...extra},'*');}
function height(){send('streamlit:setFrameHeight',{height:Math.max(800,document.documentElement.scrollHeight)});}
function pump(){if(current||!queue.length)return;current=queue.shift();send('streamlit:setComponentValue',{value:current,dataType:'json'});}
window.hseBridge=async function(path,{method='GET',data,form}={}){const request={id:crypto.randomUUID(),path,method,data:data||null,form:{},files:{},active_site:new URL(location.href).searchParams.get('hse_site')};if(form)for(const [key,value]of form.entries()){if(value instanceof File){if(value.size>15*1024*1024)throw new Error('Limite file: 15 MB');const bytes=new Uint8Array(await value.arrayBuffer());let binary='';for(let i=0;i<bytes.length;i+=32768)binary+=String.fromCharCode(...bytes.subarray(i,i+32768));request.files[key]={name:value.name,base64:btoa(binary)};}else request.form[key]=value;}
 return new Promise((resolve,reject)=>{pending.set(request.id,{resolve,reject});queue.push(request);pump();});};
window.addEventListener('message',event=>{if(event.source!==window.parent||event.data.type!=='streamlit:render')return;const args=event.data.args;
 if(lastActor!==null&&lastActor!==args.config.user){location.reload();return;}lastActor=args.config.user;
 if(!loaded){loaded=true;if(args.config.selected_site){const url=new URL(location.href);url.searchParams.set('hse_site',args.config.selected_site);history.replaceState(null,'',url);}window.HSE_CONFIG={...args.config,api:'streamlit://bridge',assets:new URL('assets/',location.href).href};const script=document.createElement('script');script.src='assets/app.bundle.js';document.body.append(script);new ResizeObserver(height).observe(document.body);}
 for(const response of args.responses||[]){const p=pending.get(response.id);if(!p)continue;pending.delete(response.id);if(response.error){const e=new Error(response.error.message);e.field=response.error.details?.field;e.current=response.error.status===409?response.error.details:null;p.reject(e);}else p.resolve(response.data);if(current?.id===response.id){current=null;pump();}}
 height();});
send('streamlit:componentReady',{apiVersion:1});height();
