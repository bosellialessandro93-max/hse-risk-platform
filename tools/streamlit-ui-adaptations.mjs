import fs from 'node:fs';
export function adaptUI(code){
 const replace=(a,b)=>{if(!code.includes(a))throw Error('UI boundary changed: '+a.slice(0,80));code=code.replace(a,b);};
 replace("for(const s of schemas[kind]||[])","for(const s of editorSchemas(kind,d))");
 replace("schemas.assessments.forEach((s,i)","editorSchemas(kind,d).forEach((s,i)");
 replace("['month','phase'","['week','month','phase'");
 replace("r.description||r.month||r.week", "r.description||(r.kind==='assessments'?assessmentPeriod(r):r.week||r.month)");
 replace("(d.month||'Mese da indicare')", "assessmentPeriod(d)");
 replace("state.site.name+' · '+d.month", "state.site.name+' · '+assessmentPeriod(d)");
 code=code.replaceAll('Target mensile comune ispezioni','Target comune ispezioni per periodo').replaceAll('Target mensile configurabile','Target per periodo configurabile');
 const historyStart=code.indexOf('async function history(){'),historyEnd=code.indexOf('\nfunction historyChart(',historyStart),chartEnd=code.indexOf('\n',code.indexOf('return box;}',historyEnd));
 if(historyStart<0||historyEnd<0||chartEnd<0)throw Error('History UI boundary changed');
 code=code.slice(0,historyStart)+fs.readFileSync('streamlit_app/ui/period-ui.js','utf8')+code.slice(chartEnd);
 replace("if(kind==='plans')bar.append(button('Importa sinottico assistito',()=>importPanel()));", "if(kind==='plans'&&state.access?.can_write?.plans!==false){bar.prepend(button('Carica immagine sinottico',()=>importPanel(),true));main.append(el('p',{class:'notice'},'Parti da una foto o screenshot: estrai i contenuti, rivedi la lista compilata e completa la bozza prima di salvarla.'));}");
 // Import is also available at the top of a new plan, without silently replacing an existing draft.
 replace("if(kind==='meetings'&&d.source_snapshot)","if(kind==='plans'&&!d.id&&writable)main.append(button('Carica immagine sinottico',async()=>{if(state.dirty&&!window.confirm('Le modifiche non salvate restano nella bozza locale. Aprire l’importazione?'))return;await importPanel();}));\n if(kind==='meetings'&&d.source_snapshot)");
 // Existing advanced mapping/review is retained as the fallback for unknown or ambiguous layouts.
 replace("Le colonne vanno mappate e ogni campo verificato.","Il riconoscimento delle intestazioni propone i campi; verifica sempre la lista. Per tabelle diverse usa la mappatura manuale.");
 replace("card.append(cg,button('Estrai pagina", "card.append(button('Compila automaticamente da immagine',async()=>{if(!page.enabled)throw Error('Pagina esclusa');const words=await recognize(page,(v)=>{progress.value=v;},abort.signal);const inferred=inferSynoptic(words,page.canvas.width,page.canvas.height);const boundaries=gridRows(page.canvas).filter(y=>y>inferred.headerBottom);const rows=structure(inferred.words,inferred.columns,page.page,page.canvas.width,boundaries.length>=2?boundaries:[],page.canvas.height);if(!rows.length)throw Error('Nessuna attività estratta. Verifica immagine e mappatura manuale.');const previous=proposed.filter(r=>r.provenance?.[0]?.page===page.page);proposed=proposed.filter(r=>r.provenance?.[0]?.page!==page.page);proposed.push(...mergeExtraction(previous,rows));message(`${rows.length} attività proposte. Premi Inserisci righe proposte in bozza per rivedere la lista compilata.`);},true),cg,button('Estrai pagina");
 code=code.replaceAll("geojson:chosen.geojson,", "geojson:chosen.geojson,landscape:chosen.landscape||[],map_layout:'light',").replaceAll("geojson:result.geojson,", "geojson:result.geojson,landscape:result.landscape||[],map_layout:'light',");
 replace("el('h3',{},'Tavola neutra e classificazione')","el('h3',{},'Tavola e classificazione')");
 replace("section.append(el('p',{class:'notice'},(d.import_warnings", "const layout=el('select',{id:'map-layout'},el('option',{value:'light'},'Light · geometrie e segnali'),el('option',{value:'landscape',disabled:!(d.landscape||[]).length},'Paesaggio incorporato nel KMZ'));layout.value=d.map_layout||'light';layout.onchange=()=>{d.map_layout=layout.value;markDirty();redraw();};section.append(el('label',{for:'map-layout'},'Layout mappa'),layout,el('p',{},(d.landscape||[]).length?'Il layout scelto viene conservato al salvataggio e usato negli export PNG/PDF.':'Nessun paesaggio incorporato compatibile. Le immagini di Google Earth non sono sempre incluse nel KMZ; nessuna mappa esterna viene scaricata.'));\n section.append(el('p',{class:'notice'},(d.import_warnings");
 replace("geojson:b.geojson,signs:b.signs||[],camera:b.camera", "geojson:b.geojson,landscape:b.landscape||[],map_layout:b.map_layout||'light',signs:b.signs||[],camera:b.camera");
 code=code.replaceAll('Inserisci righe proposte in bozza (non pubblica)','Rivedi lista compilata');
 return "import {inferSynoptic} from 'hse-synoptic-auto';\n"+code;
}
export function adaptSchemas(code){return code.replace("f('month','Mese *','month')","f('week','Lunedì della settimana *','date')").replace("max:31","max:7").replace("assessments:'Valutazione mensile'","assessments:'Valutazione Risk Index'").replace("f('month','Mese','month')","f('event_date','Data segnalazione','date')");}
export function adaptMap(code){
 code=code.replace("const points=[];", "const points=[];if(record.map_layout==='landscape')for(const layer of record.landscape||[]){const b=layer.bounds;points.push([b.west,b.south],[b.east,b.north]);}");
 code=code.replace("const labelBoxes=[];", "if(record.map_layout==='landscape')for(const layer of record.landscape||[]){const b=layer.bounds,[x,y]=project([b.west,b.north]),[right,bottom]=project([b.east,b.south]);add('image',{href:'data:'+layer.mime+';base64,'+layer.chunks.join(''),x,y,width:right-x,height:bottom-y,preserveAspectRatio:'none',transform:`rotate(${-b.rotation} ${(x+right)/2} ${(y+bottom)/2})`});}\n const labelBoxes=[];");
 return code.replace('Vista neutra WGS84, proiezione locale',"${record.map_layout==='landscape'?'Paesaggio KMZ':'Vista light'} WGS84, proiezione locale");
}
export function adaptExports(code){
 code=code.replace('record.month||record.week',"record.week||(record.month)");
 code=code.replace("h.month<record.month", "!!h.week===!!record.week&&(h.week||h.month)<(record.week||record.month)").replace("a.month.localeCompare(b.month)","(a.week||a.month).localeCompare(b.week||b.month)");
 const from=code.indexOf('const previous=compatible.at(-1);'),to=code.indexOf('\n',from);
 if(from<0||to<0)throw Error('Export period boundary changed');
 code=code.slice(0,from)+"const previous=compatible.at(-1);const prior=new Date((record.week||record.month+'-01')+'T12:00:00Z');if(record.week)prior.setUTCDate(prior.getUTCDate()-7);else prior.setUTCMonth(prior.getUTCMonth()-1);const adjacent=previous&&(previous.week||previous.month)===prior.toISOString().slice(0,record.week?10:7);const delta=r&&adjacent?(r.base-previous.result.base).toFixed(2)+' punti dal periodo precedente':'Variazione non disponibile: periodo precedente assente o non comparabile';"+code.slice(to);
 return code.replace("h.month+':'", "(h.week||h.month)+':'").replace("h.month+': '","(h.week||h.month)+': '").replace('Nessun mese precedente comparabile. Mesi mancanti','Nessun periodo precedente comparabile. Periodi mancanti');
}
