import {build} from 'esbuild';
import fs from 'node:fs';
import path from 'node:path';
const source='hse-risk-platform/assets',destination='streamlit_app/frontend/assets';
fs.mkdirSync(destination,{recursive:true});
function copy(src,dst){
 if(fs.statSync(src).isDirectory()){
  fs.mkdirSync(dst,{recursive:true});for(const name of fs.readdirSync(src))copy(src+'/'+name,dst+'/'+name);
 }else{
  if(fs.existsSync(dst)&&fs.readFileSync(src).equals(fs.readFileSync(dst)))return;
  // Existing build outputs may be hard links: replace before writing, never modify in place.
  if(fs.existsSync(dst))fs.unlinkSync(dst);
  fs.copyFileSync(src,dst);
 }
}
for(const name of ['vendor','fonts','images','app.css','standalone.css'])if(fs.existsSync(source+'/'+name))copy(source+'/'+name,destination+'/'+name);
for(const name of ['LICENSE','THIRD_PARTY_LICENSES.txt'])copy('hse-risk-platform/'+name,'streamlit_app/frontend/'+name);
copy('streamlit_app/ui/design.css',destination+'/design.css');
const brand=JSON.parse(fs.readFileSync('streamlit_app/ui/brand.json','utf8'));
const slots=['logo','home','dashboard_hse','dashboard_company','assessment','output','profiles','wind','solar','bess'];
for(const [slot,entry] of Object.entries(brand)){
 if(!slots.includes(slot)||!entry||!(/^[a-z0-9][a-z0-9._-]*\.(png|jpe?g|webp|svg)$/i).test(entry.file)||typeof entry.alt!=='string'||!entry.alt.trim())throw new Error('Invalid approved brand asset: '+slot);
 fs.mkdirSync(destination+'/brand',{recursive:true});
 copy('streamlit_app/ui/references/'+entry.file,destination+'/brand/'+entry.file);
}
let code=fs.readFileSync(source+'/app.js','utf8');
function replaceOnce(before,after){if(!code.includes(before))throw new Error('Streamlit adaptation boundary changed: '+before.slice(0,80));code=code.replace(before,after);}
const start=code.indexOf('async function api('),end=code.indexOf('async function list(',start);
if(start<0||end<0)throw new Error('API boundary changed');
code=code.slice(0,start)+'const api=window.hseBridge;\n'+code.slice(end);
replaceOnce("const root=document.getElementById('hse-platform');", `
const brand=${JSON.stringify(brand)};
function brandImage(slot){const item=brand[slot];return item?el('img',{class:'approved-reference','data-image-slot':slot,src:HSE_CONFIG.assets+'brand/'+item.file,alt:item.alt,decoding:'async'}):null;}
const root=document.getElementById('hse-platform');`);
replaceOnce("el('h1',{},'HSE Risk Platform')", "brandImage('logo'),el('h1',{},'HSE Risk Platform')");
replaceOnce("root.dataset.role=companyPath?'company':'hse';", "root.dataset.role=companyPath?'company':'hse';root.dataset.view=state.view;root.dataset.technology=state.site?.technology||'';");
replaceOnce("el('div',{class:'hero-technologies'}", "brandImage(company?'dashboard_company':'dashboard_hse')||el('div',{class:'hero-technologies'}");
replaceOnce("function sitesView(){", "function sitesView(){const reference=brandImage('home');if(reference)body().append(reference);");
replaceOnce("async function assessmentTools(d,main,bar,writable){", "async function assessmentTools(d,main,bar,writable){const reference=brandImage(d.result?'output':'assessment');if(reference)main.append(reference);");
replaceOnce("import {download,exportRecord,ics,exportMapPDF} from './exports';",`
import {download,ics} from 'hse-light-downloads';
const exportRecord=(...args)=>import('./exports').then(m=>m.exportRecord(...args));
const exportMapPDF=(...args)=>import('./exports').then(m=>m.exportMapPDF(...args));`);
replaceOnce("for(const k of ['areas','companies'])if(!state.data[k])await list(k);", "await Promise.all(['areas','companies'].filter(k=>!state.data[k]).map(k=>list(k)));");
replaceOnce("const cap=await api('capabilities');", 'const cap=state.access;');
replaceOnce("for(const k of company?['observations','plans']:['observations','plans','actions']){try{const rs=await list(k);", "await Promise.all((company?['observations','plans']:['observations','plans','actions']).map(async k=>{try{const rs=await api(`${k}?site_id=${state.site.id}&per_page=1&page=1`);");
replaceOnce('String(rs.length)', 'String(rs.total)');
replaceOnce("catch(e){counts.append(el('p',{},e.message));}}main.append(counts", "catch(e){counts.append(el('p',{},e.message));}}));main.append(counts");
// Explicit slots preserve the existing illustrations until approved references are supplied.
replaceOnce("src:HSE_CONFIG.assets+'images/'+technology.toLowerCase()+'.svg'", "'data-image-slot':technology.toLowerCase(),src:HSE_CONFIG.assets+(brand[technology.toLowerCase()]?'brand/'+brand[technology.toLowerCase()].file:'images/'+technology.toLowerCase()+'.svg')");
code=code.replaceAll("class:'card technology-card'},technologyImage(technology)", "class:'card technology-card','data-technology':technology},technologyImage(technology)");
code=code.replaceAll("class:'card technology-card'},technologyImage(site.technology)", "class:'card technology-card','data-technology':site.technology},technologyImage(site.technology)");
const exportsSource=fs.readFileSync(source+'/exports.js','utf8');
const download=exportsSource.match(/^export function download\(.+$/m)?.[0];
const ics=exportsSource.match(/^export function ics\(.+$/m)?.[0];
if(!download||!ics)throw new Error('Lightweight export boundary changed');
const plugins=[{name:'streamlit-adaptations',setup(builder){
 builder.onResolve({filter:/^hse-light-downloads$/},()=>({path:'light-downloads',namespace:'hse'}));
 builder.onLoad({filter:/.*/,namespace:'hse'},()=>({contents:"const clean=s=>String(s??'Dato non disponibile');\n"+download+'\n'+ics,loader:'js'}));
 builder.onLoad({filter:/schemas\.js$/},args=>({contents:fs.readFileSync(args.path,'utf8').replaceAll('ID utente WordPress *','ID account Streamlit *'),loader:'js'}));
 builder.onLoad({filter:/importer\.js$/},args=>{
  let contents=fs.readFileSync(args.path,'utf8');
  const pdfHeader="import * as pdfjs from 'pdfjs-dist/legacy/build/pdf.mjs';\npdfjs.GlobalWorkerOptions.workerSrc=HSE_CONFIG.assets+'vendor/pdf.worker.min.mjs';";
  if(!contents.includes(pdfHeader)||!contents.includes("import {createWorker} from 'tesseract.js';"))throw new Error('Importer boundary changed');
  contents=contents.replace(pdfHeader,'').replace("import {createWorker} from 'tesseract.js';",'');
  contents=contents.replace("if(file.type==='application/pdf'){", "if(file.type==='application/pdf'){const pdfjs=await import('pdfjs-dist/legacy/build/pdf.mjs');pdfjs.GlobalWorkerOptions.workerSrc=HSE_CONFIG.assets+'vendor/pdf.worker.min.mjs';");
  contents=contents.replace("try{worker=await createWorker(", "try{const {default:{createWorker}}=await import('tesseract.js');worker=await createWorker(");
  return {contents,loader:'js'};
 });
}}];
// Remove only this builder's previous chunks; unrelated user files are left intact.
for(const name of fs.readdirSync(destination))if(/^hse-chunk-[A-Z0-9]+\.js$/.test(name))fs.unlinkSync(destination+'/'+name);
const result=await build({stdin:{contents:code,resolveDir:path.resolve(source),sourcefile:'streamlit-adapter.js'},
 outdir:destination,entryNames:'app.bundle',bundle:true,minify:true,platform:'browser',target:['es2022'],format:'esm',splitting:true,
 chunkNames:'hse-chunk-[hash]',metafile:true,define:{'process.env.NODE_ENV':'"production"'},legalComments:'eof',plugins});
fs.mkdirSync('.local',{recursive:true});fs.writeFileSync('.local/streamlit-build.json',JSON.stringify(result.metafile,null,2));
console.log('Built lazy Streamlit component; WordPress assets unchanged.');
