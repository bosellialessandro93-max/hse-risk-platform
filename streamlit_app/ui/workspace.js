/* Streamlit-only corporate workspace. Uses the existing domain and permission boundary. */
const moduleIcons={overview:'house',sites:'buildings',advisor:'lightbulb',assessments:'clipboard-text',events:'warning-circle',actions:'list-checks',plans:'users-three',calendar:'calendar-blank',observations:'camera',meetings:'chats-circle',toolboxes:'toolbox',sessions:'users',checklists:'check-square',documents:'files',maps:'map-trifold',history:'chart-bar',archive:'archive',ai:'sparkle'};
function icon(name){return el('img',{class:'ui-icon',src:HSE_CONFIG.assets+'icons/'+name+'.svg',alt:'','aria-hidden':'true',width:22,height:22});}
function iconButton(text,name,action,primary=false){const b=button(text,action,primary);b.prepend(icon(name));return b;}
function corporateNavButton(view){return el('button',{type:'button','aria-current':state.view===view?'page':null,onclick:()=>run(async()=>{state.navOpen=false;navLayout();await change(view);})},icon(moduleIcons[view]||'squares-four'),labels[view]||view);}
function refreshCorporateHeader(company){
 const nav=root.querySelector('#corporate-primary');if(!nav)return;
 const items=company?[['overview','Home','house'],['plans','Sinottici','users-three'],['calendar','Calendario','calendar-blank'],['observations','Sopralluoghi','camera']]:[['overview','Home','house'],['sites','Cantieri','buildings'],['assessments','Assessment','clipboard-text'],['history','Output','chart-bar']];
 const ai=iconButton('Assistenza AI','sparkle',()=>change('ai'));ai.dataset.primaryView='ai';ai.setAttribute('aria-current',state.view==='ai'?'page':'false');
 nav.replaceChildren(...items.map(([view,label,name])=>{const b=iconButton(label,name,()=>change(view));b.dataset.primaryView=view;b.setAttribute('aria-current',state.view===view?'page':'false');return b;}),ai);
 root.querySelector('#corporate-actor-role').textContent=HSE_CONFIG.admin?'Amministratore':({manager:'Referente HSE',reader:'Lettura',company:'Impresa'})[state.access?.membership?.role]||'Utente';
}
async function corporateAccount(){
 if(state.dirty&&!window.confirm('Le modifiche non salvate in questo modulo non verranno inviate. Aprire la gestione account?'))return;
 await api('__ui',{method:'POST',data:{page:HSE_CONFIG.admin?'Account utenti':'Profilo'}});
}
async function init(){
 labels.ai='Assistenza AI';
 const identity=el('div',{class:'corporate-brand'},brandImage('logo'),el('div',{},el('h1',{},'HSE Risk Index'),el('p',{},'Safety assessment for Wind, Solar & BESS')));
 const actor=el('button',{type:'button',class:'corporate-actor',onclick:()=>run(corporateAccount),'aria-label':'Apri gestione account'},icon('user-circle'),el('span',{},el('strong',{},HSE_CONFIG.display_name||'Account HSE'),el('small',{id:'corporate-actor-role'},HSE_CONFIG.admin?'Amministratore':'Utente')),icon('caret-down'));
 const toggle=el('button',{id:'hse-nav-toggle',type:'button','aria-label':'Apri o chiudi i moduli','aria-controls':'hse-nav','aria-expanded':'false',onclick:()=>{state.navOpen=!state.navOpen;navLayout();}},icon('squares-four'),el('span',{},'Moduli'));
 root.replaceChildren(el('a',{class:'skip-link',href:'#hse-body'},'Vai al contenuto'),el('header',{class:'app-header corporate-header'},identity,el('nav',{id:'corporate-primary','aria-label':'Navigazione principale'}),el('div',{class:'corporate-account'},toggle,actor)),el('nav',{id:'hse-nav','aria-label':'Moduli HSE',hidden:true}),el('div',{class:'workspace-context'},el('div',{class:'toolbar',id:'hse-site'})),el('div',{id:'hse-message',role:'status','aria-live':'polite',hidden:true}),el('main',{id:'hse-body',tabindex:'-1'}));
 navLayout();const sites=await list('sites');const remembered=new URL(location.href).searchParams.get('hse_site');state.site=sites.find(s=>s.id===remembered)||sites[0]||null;await render();
}
function navLayout(){const nav=root.querySelector('#hse-nav'),toggle=root.querySelector('#hse-nav-toggle');if(!nav||!toggle)return;nav.hidden=!state.navOpen;toggle.hidden=false;toggle.setAttribute('aria-expanded',String(!nav.hidden));toggle.querySelector('span')?.replaceChildren(document.createTextNode(nav.hidden?'Moduli':'Chiudi moduli'));}
async function overview(){
 const main=body();main.classList.add('corporate-home');
 const company=state.access?.membership?.role==='company'&&!HSE_CONFIG.admin;
 main.querySelector('.breadcrumb')?.remove();main.querySelector('h2')?.remove();
 const start=()=>change(company?'plans':'assessments');
 const intro=el('div',{class:'hero-copy'},el('p',{class:'eyebrow'},'AMBIENTE · SALUTE · SICUREZZA'),company?el('h2',{},'La sicurezza inizia da una pianificazione condivisa.'):el('h2',{},'Valutiamo insieme',el('br'), 'i rischi per un’energia',el('br'),'più ',el('span',{class:'title-safety'},'sicura'),' e ',el('span',{class:'title-sustainability'},'sostenibile')),el('p',{class:'hero-description'},company?'Organizza le attività, aggiorna i sinottici e condividi le evidenze del tuo cantiere.':'HSE Risk Index ti guida nella valutazione dei rischi HSE per le attività di costruzione ed esercizio di impianti Wind, Solar e BESS, con un percorso semplice e strutturato.'),el('div',{class:'hero-actions'},iconButton(company?'Apri sinottici':'Inizia assessment','play',start,true),iconButton('Scopri il flusso','tree-structure',()=>main.querySelector('#corporate-flow').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'}))));
 const technologies=el('aside',{class:'hero-energy','aria-label':'Tecnologie supportate'},...['Wind','Solar','BESS'].map((technology,i)=>el('div',{class:'energy-item','data-technology':technology},icon(['wind','sun','battery-charging'][i]),el('div',{},el('strong',{},technology),el('small',{},'Costruzione ed esercizio')))));
 const hero=el('section',{class:'hero corporate-hero'},intro,technologies);const picture=brand[company?'dashboard_company':'dashboard_hse']||brand.home;if(picture){hero.style.backgroundImage=`url("${HSE_CONFIG.assets}brand/${picture.file}")`;hero.prepend(el('img',{class:'hero-mobile-photo',src:HSE_CONFIG.assets+'brand/'+picture.file,alt:picture.alt,width:1888,height:833,decoding:'async',fetchpriority:'high'}));}main.append(hero);
 const steps=company?[
  ['Selezione cantiere','Scegli il cantiere assegnato e verifica il contesto operativo.','buildings',()=>root.querySelector('[aria-label="Cantiere attivo"]').focus()],
  ['Pianificazione attività','Compila le attività e i riferimenti del sinottico impresa.','clipboard-text',()=>change('plans')],
  ['Verifica e conferma','Rivedi il sinottico prima della conferma esplicita.','check-square',()=>change('plans')],
  ['Calendario condiviso','Consulta le attività confermate e le evidenze di cantiere.','calendar-blank',()=>change('calendar')]
 ]:[
  ['Selezione contesto','Scegli il cantiere e la tecnologia Wind, Solar o BESS.','users-three',()=>change('sites')],
  ['Inserimento dati','Compila attività, segnalazioni, esposizione e misure di presidio.','clipboard-text',()=>change('assessments')],
  ['Analisi del rischio','Calcola e verifica indice, contributi e dati di origine.','chart-bar',()=>change('assessments')],
  ['Export report','Apri una valutazione salvata e scarica i report disponibili.','file-text',()=>change('history')]
 ];
 const flow=el('section',{id:'corporate-flow',class:'corporate-flow'},el('div',{class:'section-heading'},el('div',{},el('p',{class:'eyebrow'},'COME FUNZIONA'),el('h2',{},'Un processo semplice, dalla valutazione al report'))));
 const cards=el('div',{class:'flow-grid'});
 steps.forEach(([title,description,name,action],i)=>{const b=iconButton('Apri '+title,'arrow-right',action);b.className='flow-open';b.setAttribute('aria-label','Apri '+title);b.replaceChildren(icon('arrow-right'));cards.append(el('article',{class:'flow-card','data-step':i+1},el('div',{class:'flow-icon-row'},el('span',{class:'step-number'},String(i+1)),icon(name)),el('h3',{},title),el('p',{},description),b));});
flow.append(cards);main.append(flow);
 const benefits=el('section',{class:'corporate-benefits'},el('h3',{},'Perché HSE Risk Index'),el('div',{class:'benefit-grid'},...[
 ['shield-check','Evidenze tracciabili','Dati, revisioni e allegati collegati al cantiere.'],
 ['leaf','Wind, Solar e BESS','Un ambiente comune per le tre tecnologie.'],
 ['gear-six','Metodo riproducibile','Contributi, risultati e modello sempre consultabili.'],
 ['users-three','Ruoli e permessi','Accesso ai dati secondo le assegnazioni effettive.']
 ].map(([name,title,description])=>el('article',{},icon(name),el('div',{},el('h4',{},title),el('p',{},description))))));main.append(benefits);
 const counts=el('section',{class:'dashboard-records'},el('div',{class:'section-heading'},el('div',{},el('p',{class:'eyebrow'},'IL TUO SPAZIO OPERATIVO'),el('h2',{},company?'Attività della tua impresa':'Dati del cantiere'))));
 const grid=el('div',{class:'grid kpi-grid'});counts.append(grid);main.append(counts);
 await Promise.all((company?['observations','plans']:['observations','plans','actions']).map(async kind=>{try{const result=await api(`${kind}?site_id=${state.site.id}&per_page=1&page=1`);grid.append(el('article',{class:'card kpi'},icon(moduleIcons[kind]),el('h3',{},labels[kind]),el('p',{class:'kpi-value'},String(result.total)),el('p',{},'Record accessibili'),button('Apri',()=>change(kind))));}catch(error){grid.append(el('p',{class:'error'},error.message));}}));
 main.append(el('p',{class:'model-note'},'Modello 2.0.0 · Calcolo temporaneo e salvataggio esplicito. L’indice è un indicatore gestionale, distinto dalla probabilità di infortunio.'));
}
async function assistantPage(){
 const main=body();main.classList.add('corporate-assistant');
 main.append(el('p',{class:'page-intro'},'Analisi assistita di NC, estratti documentali, risultati e raccomandazioni. Nessuna modifica automatica a dati o Risk Index.'));
 const status=await api('__assistant',{method:'POST',data:{operation:'status'}});
 const badges=el('div',{class:'ai-status'},el('span',{class:'badge'},status.ready?'Configurazione presente':'Configurazione necessaria'),el('span',{class:'badge'},status.key_present?'Chiave presente nei Secrets':'Chiave non configurata'),el('span',{class:'badge'},status.confidential_authorized?'Trattamento riservati autorizzato':'Dati riservati bloccati'));
 main.append(badges);
 if(status.ready)main.append(el('p',{class:'field-help'},'La presenza della chiave non conferma ancora l’accesso a Google o la disponibilità della quota.'),iconButton('Verifica collegamento','check-square',async()=>{const checked=await api('__assistant',{method:'POST',data:{operation:'check_connection'}});message(checked.message);}));
 if(!status.ready){const notice=el('section',{class:'card'},el('h3',{},status.key_present?'Abilita Google Gemini':'Collega Google Gemini'),el('p',{},HSE_CONFIG.admin?'Aggiungi la chiave e abilita Gemini nei Secrets dell’app Streamlit. Non modificare la configurazione Neon esistente.':'L’amministratore deve completare la configurazione nei Secrets Streamlit. Nessun dato viene trasmesso.'));
  if(HSE_CONFIG.admin)notice.append(el('details',{},el('summary',{},'Istruzioni per i Secrets Streamlit'),el('p',{},'Apri Manage app → Settings → Secrets. Se la sezione [gemini] esiste già, aggiornala senza duplicarla; altrimenti aggiungila in fondo al file. Mantieni invariate le sezioni database e autenticazione. Inserisci la chiave solo in quell’editor e salva.'),el('pre',{},'[gemini]\nenabled = true\n'+(status.key_present?'':'api_key = "INSERISCI_LA_CHIAVE_NELL_EDITOR_SECRETS"\n')+'model = "gemini-2.5-flash"\nprocessing_authorized = false\nallow_confidential_data = false'),el('p',{},'Sono supportate anche Gemini API Key, GEMINI_API_KEY o GOOGLE_API_KEY già presenti nei Secrets. L’abilitazione richiede comunque [gemini] enabled = true.')));
  main.append(notice);
 }
 const form=el('form',{class:'card ai-form'}),task=el('select',{id:'ai-task'},...['Analisi NC','Lettura documenti','Spiegazione indice','Raccomandazioni'].map(t=>el('option',{value:t},t)));
 const classification=el('select',{id:'ai-classification'},el('option',{value:'public'},'Dati pubblici'),el('option',{value:'synthetic'},'Dati sintetici di collaudo'));
 if(status.confidential_authorized)classification.append(el('option',{value:'confidential'},'Dati riservati: trattamento autorizzato'));
 const text=el('textarea',{id:'ai-text',rows:9,maxlength:20000,placeholder:'Incolla soltanto il testo che vuoi analizzare. Nessun record o documento viene caricato automaticamente.'});
 const consent=el('input',{id:'ai-consent',type:'checkbox'}),result=el('section',{class:'ai-answer',hidden:true,'aria-live':'polite'});
 const send=el('button',{type:'submit',class:'primary'},icon('sparkle'),'Invia il testo a Gemini');send.disabled=!status.ready;
 form.append(el('div',{class:'grid'},el('label',{for:'ai-task'},'Attività assistita',task),el('label',{for:'ai-classification'},'Classificazione del testo',classification)),el('label',{for:'ai-text'},'Testo da analizzare',text),el('label',{for:'ai-consent',class:'check'},consent,'Confermo la classificazione e autorizzo questo invio a Google Gemini.'),el('p',{class:'field-help'},'Non inserire credenziali o dati personali. Verifica sempre la risposta prima di utilizzarla.'),send);
 let busy=false;
 form.addEventListener('submit',event=>{event.preventDefault();if(busy||!status.ready)return;run(async()=>{
  if(!text.value.trim()||!consent.checked)throw new Error('Inserisci il testo e conferma esplicitamente l’invio.');
  result.hidden=true;busy=true;send.disabled=true;send.setAttribute('aria-busy','true');
  try{const response=await api('__assistant',{method:'POST',data:{operation:'generate',task:task.value,text:text.value,classification:classification.value,consent:consent.checked}});consent.checked=false;result.hidden=false;result.replaceChildren(el('h3',{},'Suggerimento da verificare'),el('p',{},'Risposta generata da Gemini. Nessun dato è stato salvato o modificato.'),el('pre',{},response.text));}
  finally{busy=false;send.disabled=false;send.removeAttribute('aria-busy');}
 });});main.append(form,result);
}
