// Infer only recognized table headers and explicit dates. Unknown layouts retain manual mapping.
export function inferSynoptic(words,width,height){
 const fields=[['description',/^(descrizione|attivit[aà]|lavorazion[ei])$/i],['supervisor',/^prepost[oi]$/i],['contact',/^(contatto|telefono)$/i],['pos',/^pos\b/i],['equipment',/^mezzi$/i],['area_name',/^(area|wtg)$/i],['contractor',/^affidataria$/i],['executor',/^esecutrice$/i],['conditions',/^(condizioni|interferenze)$/i]];
 const lines=[];for(const w of [...words].sort((a,b)=>a.bbox.y0-b.bbox.y0)){let line=lines.find(l=>Math.abs(l.y-w.bbox.y0)<Math.max(8,(w.bbox.y1-w.bbox.y0)*.65));if(!line){line={y:w.bbox.y0,words:[]};lines.push(line);}line.words.push(w);}
 const identify=w=>fields.find(([,re])=>re.test(w.text.trim().replace(/[:*]$/,'')))?.[0];
 const header=lines.find(l=>l.words.some(w=>identify(w)==='description')&&l.words.some(w=>identify(w)==='supervisor'));
 if(!header)throw Error('Intestazioni Attività/Descrizione e Preposto non riconosciute: usa la mappatura manuale sotto. Nessun campo è stato inventato.');
 const found=[],seen=new Set();for(const w of header.words.sort((a,b)=>a.bbox.x0-b.bbox.x0)){
  let field=identify(w),date;
  const m=w.text.match(/^(\d{2})[/.](\d{2})[/.](\d{4})$/);if(m)date=`${m[3]}-${m[2]}-${m[1]}`;else if(/^\d{4}-\d{2}-\d{2}$/.test(w.text))date=w.text;
  if(date&&new Date(date+'T12:00:00Z').toISOString().slice(0,10)===date)field='operators';
  if(!field||seen.has(field+(date||'')))continue;seen.add(field+(date||''));found.push({field,date,x:w.bbox.x0});
 }
 const columns=found.map((f,i)=>({field:f.field,...(f.date?{date:f.date}:{}),from:i?Math.max(0,(f.x-12)/width*100):0,to:i<found.length-1?Math.max(0,(found[i+1].x-12)/width*100):100}));
 const bottom=Math.max(...header.words.map(w=>w.bbox.y1));return {columns,words:words.filter(w=>w.bbox.y0>bottom+2),headerBottom:bottom/height*100};
}
