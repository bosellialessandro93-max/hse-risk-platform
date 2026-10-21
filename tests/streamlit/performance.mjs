// Real Streamlit transport against a dedicated local QA database; never production.
import {chromium} from '@playwright/test';
import fs from 'node:fs';
import {performance} from 'node:perf_hooks';
const qa=process.env.HSE_QA_DIR||'.local/streamlit-postgres-qa';
const auth=JSON.parse(JSON.parse(fs.readFileSync(qa+'/streamlit-test-env.json')).HSE_AUTH);
const browser=await chromium.launch({executablePath:process.env.HSE_CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox']});
const samples=[];
try {
 for(let i=0;i<5;i++) {
  const context=await browser.newContext({viewport:{width:1440,height:1000}});
  const page=await context.newPage();
  const failures=[];
  page.on('pageerror',e=>failures.push(e.message));
  await page.addInitScript(()=>{
   window.__bridgeMessages=0;
   window.addEventListener('message',e=>{if(e.data?.type==='streamlit:setComponentValue')window.__bridgeMessages++;});
  });
  await page.goto('http://127.0.0.1:8505');
  await page.getByLabel('Nome utente',{exact:true}).fill(auth.bootstrap_username);
  await page.getByLabel('Password',{exact:true}).fill(auth.bootstrap_password);
  const start=performance.now();
  await page.getByRole('button',{name:'Accedi',exact:true}).click();
  const iframe=page.locator('iframe[title*="hse_workspace"]');
  await iframe.waitFor({timeout:60000});
  const frame=await (await iframe.elementHandle()).contentFrame();
  await frame.locator('.kpi').nth(2).waitFor({timeout:60000});
  const dashboard_ms=performance.now()-start;
  const initial=await frame.evaluate(()=>({
   js_bytes:performance.getEntriesByType('resource').filter(r=>new URL(r.name).pathname.endsWith('.js')).reduce((n,r)=>n+r.decodedBodySize,0),
   scripts:performance.getEntriesByType('resource').filter(r=>new URL(r.name).pathname.endsWith('.js')).length
  }));
  const dashboard_messages=await page.evaluate(()=>window.__bridgeMessages);
  const navigation={};
  for(const view of ['observations','plans','assessments','calendar','history','overview']) {
   const tick=performance.now();
   await frame.evaluate(async v=>{await HSE_TEST.change(v);},view);
   navigation[view]=performance.now()-tick;
  }
  if(failures.length)throw new Error(failures.join('\n'));
  samples.push({dashboard_ms,dashboard_messages,...initial,navigation});
  await context.close();
 }
 const median=values=>[...values].sort((a,b)=>a-b)[Math.floor(values.length/2)];
 const summary={dashboard_ms:median(samples.map(s=>s.dashboard_ms)),dashboard_messages:median(samples.map(s=>s.dashboard_messages)),initial_js_bytes:median(samples.map(s=>s.js_bytes)),navigation_ms:Object.fromEntries(Object.keys(samples[0].navigation).map(k=>[k,median(samples.map(s=>s.navigation[k]))]))};
 const report={context:'Local Chromium, Streamlit and dedicated PostgreSQL; five new browser contexts, no WAN/Neon production measurement',samples,median:summary};
 fs.writeFileSync(process.env.HSE_PERF_OUTPUT||'tests/artifacts/streamlit-performance.json',JSON.stringify(report,null,2));
 console.log(JSON.stringify(summary));
}finally{await browser.close();}
