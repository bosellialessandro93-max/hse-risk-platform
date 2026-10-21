import vm from 'node:vm';
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {webcrypto} from 'node:crypto';
const messages=[],listeners={};
const parent={postMessage:m=>messages.push(m)};
const window={parent,addEventListener:(name,handler)=>{listeners[name]=handler;}};
const context=vm.createContext({window,crypto:webcrypto,URL,Map,File:class File{},Uint8Array,setTimeout,
 requestAnimationFrame:fn=>setTimeout(fn,0),
 location:{href:'http://localhost/component/?hse_site=site-a',reload:()=>{}},history:{replaceState:()=>{}},
 document:{documentElement:{scrollHeight:800},body:{append:()=>{},getBoundingClientRect:()=>({height:800})},createElement:()=>({}),querySelector:()=>({})},
 ResizeObserver:class{observe(){}}});
vm.runInContext(fs.readFileSync('streamlit_app/frontend/bridge.js','utf8'),context);
const flush=()=>new Promise(resolve=>setTimeout(resolve,10));
const requests=()=>messages.filter(m=>m.type==='streamlit:setComponentValue');
function respond(sent,data,error){listeners.message({source:parent,data:{type:'streamlit:render',args:{config:{user:1},responses:[{id:sent.id,...(error?{error}:{data})}]}}});}
const a=window.hseBridge('areas?site_id=a'),duplicate=window.hseBridge('areas?site_id=a'),b=window.hseBridge('companies?site_id=a');
assert.equal(a,duplicate,'Only identical in-flight GETs may be shared');
await flush();let sent=requests().at(-1).value;
assert.equal(sent.path,'__batch');assert.equal(sent.requests.length,2);
respond(sent,[{id:sent.requests[0].id,data:{items:[]}},{id:sent.requests[1].id,error:{message:'Denied',status:403}}]);
assert.deepEqual(JSON.parse(JSON.stringify(await a)),{items:[]});
await assert.rejects(b,/Denied/);
await flush();
const readBefore=window.hseBridge('sites');
const write=window.hseBridge('sites',{method:'POST',data:{name:'synthetic'}});
const readAfter=window.hseBridge('sites');
assert.notEqual(readBefore,readAfter,'Writes must invalidate in-flight deduplication across the barrier');
await flush();sent=requests().at(-1).value;assert.equal(sent.method,'GET');assert.equal(sent.requests,undefined);respond(sent,{before:true});await readBefore;
await flush();sent=requests().at(-1).value;assert.equal(sent.method,'POST');respond(sent,{saved:true});await write;
await flush();sent=requests().at(-1).value;assert.equal(sent.method,'GET');respond(sent,{after:true});await readAfter;
const again=window.hseBridge('sites');await flush();sent=requests().at(-1).value;assert.equal(sent.method,'GET');respond(sent,{fresh:true});await again;
const c=window.hseBridge('areas'),d=window.hseBridge('companies');await flush();sent=requests().at(-1).value;
respond(sent,null,{message:'Runtime unavailable',status:503});await assert.rejects(c,/Runtime unavailable/);await assert.rejects(d,/Runtime unavailable/);
console.log('PASS bridge: in-flight deduplication, read batching, per-item errors, write barriers, fresh reads and batch failures.');
