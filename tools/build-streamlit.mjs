import {build} from 'esbuild';
import fs from 'node:fs';import path from 'node:path';
const source='hse-risk-platform/assets',destination='streamlit_app/frontend/assets';fs.mkdirSync(destination,{recursive:true});
function copy(src,dst){if(fs.statSync(src).isDirectory()){fs.mkdirSync(dst,{recursive:true});for(const name of fs.readdirSync(src))copy(src+'/'+name,dst+'/'+name);}else {if(fs.existsSync(dst)&&fs.readFileSync(src).equals(fs.readFileSync(dst)))return;if(fs.existsSync(dst))fs.unlinkSync(dst);try{fs.linkSync(src,dst);}catch{fs.copyFileSync(src,dst);}}}
for(const name of ['vendor','fonts','images','app.css','standalone.css'])if(fs.existsSync(source+'/'+name))copy(source+'/'+name,destination+'/'+name);
for(const name of ['LICENSE','THIRD_PARTY_LICENSES.txt'])copy('hse-risk-platform/'+name,'streamlit_app/frontend/'+name);
let code=fs.readFileSync(source+'/app.js','utf8');const start=code.indexOf('async function api('),end=code.indexOf('async function list(',start);if(start<0||end<0)throw new Error('API boundary changed');code=code.slice(0,start)+'const api=window.hseBridge;\n'+code.slice(end);
await build({stdin:{contents:code,resolveDir:path.resolve(source),sourcefile:'streamlit-adapter.js'},outfile:destination+'/app.bundle.js',bundle:true,minify:true,platform:'browser',target:['es2022'],define:{'process.env.NODE_ENV':'"production"'},legalComments:'eof',plugins:[{name:'streamlit-labels',setup(builder){builder.onLoad({filter:/schemas\.js$/},args=>({contents:fs.readFileSync(args.path,'utf8').replaceAll('ID utente WordPress *','ID account Streamlit *'),loader:'js'}));}}]});
console.log('Built Streamlit component; WordPress assets unchanged.');
