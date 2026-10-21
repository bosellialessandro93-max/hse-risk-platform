import assert from 'node:assert/strict';import fs from 'node:fs';import {adaptMap,adaptExports,adaptSchemas} from '../../tools/streamlit-ui-adaptations.mjs';
const {inferSynoptic}=await import('data:text/javascript;base64,'+Buffer.from(fs.readFileSync('streamlit_app/ui/synoptic-auto.js')).toString('base64'));
const w=(text,x,y)=>({text,bbox:{x0:x,y0:y,x1:x+70,y1:y+20}});
const words=[w('Descrizione',10,10),w('attività',100,10),w('Preposto',400,10),w('POS',700,10),w('21/10/2026',850,10),w('Scavo',10,90),w('Mario',400,90),w('POS123',700,90),w('3',850,90)];
const inferred=inferSynoptic(words,1100,200);assert.deepEqual(inferred.columns.map(c=>c.field),['description','supervisor','pos','operators']);assert.equal(inferred.columns.at(-1).date,'2026-10-21');assert.equal(inferred.words.length,4);assert.throws(()=>inferSynoptic([w('testo senza intestazioni',10,10)],1100,200),/mappatura manuale/);
const noDate=inferSynoptic(words.filter(word=>!word.text.includes('/')),1100,200);assert.ok(noDate.columns.every(c=>c.field!=='operators'));
const schemas=adaptSchemas(fs.readFileSync('hse-risk-platform/assets/schemas.js','utf8'));assert.ok(schemas.includes("assessments:'Valutazione Risk Index'"));assert.ok(schemas.includes("f('week','Lunedì della settimana *','date')"));
const exports=adaptExports(fs.readFileSync('hse-risk-platform/assets/exports.js','utf8'));assert.ok(exports.includes('previous.week||previous.month'));assert.ok(exports.includes('prior.setUTCDate(prior.getUTCDate()-7)'));
const map=adaptMap(fs.readFileSync('hse-risk-platform/assets/map.js','utf8'));assert.ok(map.includes("record.map_layout==='landscape'"));assert.ok(map.includes('layer.chunks.join'));console.log('PASS recognized headers, explicit dates only, unknown-layout fallback and weekly/map export adaptations');
