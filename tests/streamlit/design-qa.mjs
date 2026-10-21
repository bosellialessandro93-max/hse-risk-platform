import {chromium,expect} from '@playwright/test';
import fs from 'node:fs';
const qa=process.env.HSE_QA_DIR||'.local/streamlit-postgres-qa';
const auth=JSON.parse(JSON.parse(fs.readFileSync(qa+'/streamlit-test-env.json')).HSE_AUTH);
const ids=JSON.parse(fs.readFileSync(qa+'/streamlit-test-ids.json'));
const browser=await chromium.launch({executablePath:process.env.HSE_CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox']});
const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[],reports=[];
page.on('pageerror',e=>errors.push(e.message));
try{
 await page.goto('http://127.0.0.1:8505/?hse_site='+ids.site_id);
 await page.getByLabel('Nome utente',{exact:true}).fill(auth.bootstrap_username);
 await page.getByLabel('Password',{exact:true}).fill(auth.bootstrap_password);
 await page.getByRole('button',{name:'Accedi',exact:true}).click();
 const iframe=page.locator('iframe[title*="hse_workspace"]');await iframe.waitFor();
 const frame=await (await iframe.elementHandle()).contentFrame();
 await frame.locator('.kpi').nth(2).waitFor({timeout:60000});
 const views=['overview','sites','advisor','assessments','events','actions','plans','calendar','observations','meetings','toolboxes','sessions','checklists','documents','maps','history','archive'];
 for(const width of [375,1440]){
  await page.setViewportSize({width,height:1000});
  await frame.addScriptTag({path:'node_modules/axe-core/axe.min.js'});
  for(const view of views){
   await frame.evaluate(v=>HSE_TEST.change(v),view);
   await expect(frame.locator('#hse-body h2').first()).toBeVisible();
   const result=await frame.evaluate(async()=>{
    const root=document.querySelector('#hse-platform');
    const a=await axe.run(root,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});
    return {overflow:root.scrollWidth-root.clientWidth,violations:a.violations.map(v=>({id:v.id,targets:v.nodes.map(n=>n.target)}))};
   });
   reports.push({width,view,...result});
   if(result.overflow>2||result.violations.length)throw new Error(JSON.stringify(reports.at(-1)));
   if(['overview','calendar','history','archive'].includes(view))await page.screenshot({path:`tests/artifacts/design-${view}-${width}.png`,fullPage:true});
  }
 }
 for(const width of [320,768,1024,1440]){
  await page.setViewportSize({width,height:1000});
  await frame.evaluate(async id=>HSE_TEST.edit('assessments',await HSE_TEST.api('assessments/'+id)),ids.assessment_id);
  const dimensions=await frame.locator('#hse-platform').evaluate(e=>[e.clientWidth,e.scrollWidth]);
  if(dimensions[1]>dimensions[0]+2)throw new Error('Assessment overflow '+width);
  await page.screenshot({path:`tests/artifacts/design-assessment-${width}.png`,fullPage:true});
 }
 // The optional AI screen must be useful and inert without a key or activation.
 await frame.getByRole('button',{name:'Assistenza AI',exact:true}).click();
 await expect(frame.getByText('Chiave non configurata',{exact:true})).toBeVisible();
 await expect(frame.getByRole('button',{name:'Invia il testo a Gemini'})).toBeDisabled();
 if(errors.length)throw new Error(errors.join('\n'));
 fs.writeFileSync('tests/artifacts/streamlit-design-qa.json',JSON.stringify({reports,errors,assessment_widths:[320,768,1024,1440],gemini_disabled:true},null,2));
 console.log('PASS 17 module views at 375/1440px: no overflow or axe violations; assessment at 320/768/1024/1440px; Gemini disabled.');
}finally{await browser.close();}
