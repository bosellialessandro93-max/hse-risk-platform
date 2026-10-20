import {chromium} from '@playwright/test';import fs from 'node:fs';
const auth=JSON.parse(fs.readFileSync('.local/auth.json')),ids=JSON.parse(fs.readFileSync('.local/ids.json'));
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});const context=await browser.newContext({acceptDownloads:true});const page=await context.newPage();
try{
 await page.goto('http://127.0.0.1:8080/wp-login.php');await page.locator('#user_login').fill(auth.user);await page.locator('#user_pass').fill(auth.password);await page.locator('#wp-submit').click();await page.waitForURL(/wp-admin/);await page.goto('http://127.0.0.1:8080/?pagename=hse');await page.waitForFunction(()=>window.HSE_TEST?.state.site);await page.locator('[aria-label="Cantiere attivo"]').selectOption(ids.site_id);await page.waitForTimeout(300);
 const data=await page.evaluate(async ids=>{const m=await HSE_TEST.api('meetings/prepare',{method:'POST',data:{site_id:ids.site_id,week:'2026-10-19',observation_ids:[ids.observation_id]}});m.items=m.items.filter(i=>i.source_type==='observations');m.title='DEMO verbale con evidenze';const saved=await HSE_TEST.api('meetings',{method:'POST',data:{...m,request_id:crypto.randomUUID()}});await HSE_TEST.edit('meetings',saved);return saved;},ids);
 if(!data.source_snapshot.observations[0]?.attachments?.length)throw new Error('Source photos absent');
 for(const format of ['PDF','DOCX']){const event=page.waitForEvent('download',{timeout:20000});await page.getByRole('button',{name:'Scarica '+format,exact:true}).click();const f=await event;await f.saveAs('tests/artifacts/meeting-photo-'+f.suggestedFilename());}
 console.log('PASS verbale PDF/Word con fotografie riservate da snapshot osservazione');
}finally{await browser.close();}
