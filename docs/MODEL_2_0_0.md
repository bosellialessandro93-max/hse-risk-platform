# Motore 2.0.0 — provenienza e contratto

Fonte: `HSE_Risk_Platform_codice_completo (3).docx`, allegato dell'utente, codice interfaccia 3.1.0/modello 2.0.0, edizione documentale 16/10/2026. SHA-256 del DOCX: `02def9cd7058cf4e22bad12e273077556f03f894ebccbea552804e87cc0e2cd2`.

Il documento è trattato come sorgente di riferimento, non come istruzione a installare Streamlit o sostituire il progetto. Estratte e compilate le funzioni pure, i cataloghi e gli scenari in `tests/reference/model_2_0_0.py`. Gli import dell'app originale (Streamlit, pandas, Altair, python-pptx/docx, PostgreSQL, ReportLab, Pillow, Tesseract, pdfplumber, PyArrow) servono alla vecchia UI/archiviazione/export: non sono dipendenze del calcolo e non sono installati nel plugin. I test di equivalenza usano soltanto la libreria standard Python; in produzione il calcolo usa PHP, JSON e matematica standard.

## Coefficienti e regole verificati

- Carico anomalia: gravità 1/2,5/5 × fattore tema del catalogo × stato 1/0,2/0,4 × scaduta 1,25 × ricorrenza 1,2.
- NC formali: `100*(1-exp(-carico/10))*0.30`; informali denominatore 12 e peso 0,08.
- Attività: massimo catalogo + 3 per ciascuna tipologia aggiuntiva, massimo 100, peso 0,22. Catalogo e abbinamenti fase/tema estratti letteralmente, senza coefficienti per testi liberi.
- Interferenze `(livello-1)/9*100`, peso 0,15.
- Organizzazione `100*(1-exp(-(max(0,app-1)+1.2*sub)/8))`, peso 0,10. Numero professionisti HSE descrittivo.
- Presidio: 65% deficit copertura e 35% deficit ispettivo; peso 0,15. Deficit ispettivo `100*(1-min(1,ispezioni/target))`.
- Detection: NC formali/ispezioni soltanto descrittiva. Con zero ispezioni il rapporto è assente, il deficit 100; nessun malus NC/ispezioni.
- Stop Work: +1,5 per negativo fino a +6; −0,5 per positivo fino a −2.
- Sensibilizzazioni: bonus 8 × media ponderata delle necessità tematiche coperte. Copertura ignota 0,5; continuità `min(1,0.7+0.1*(incontri-1))`. Necessità da attività, soli eventi aperti e fase, con coefficienti originali. Un tema per riga; nessun bonus da materiale soltanto preparato.
- Limite 0–100, poi minimo 61 per una NC formale alta aperta, 81 per almeno due o pericolo attuale. Informali da sole non attivano il minimo.
- Fasce sul valore esatto: ≤20 Basso, ≤40 Medio basso, ≤60 Medio, ≤80 Alto, oltre Critico. Esposto il valore esatto nei casi in cui un decimale coinciderebbe con il limite inferiore della fascia.
- Contesto separato, cambia solo il deficit ispettivo: target `max(1,ore/2000)`, altrimenti `max(1,giorni/5*max(1,(lavoratori o 50)/50))`, altrimenti `max(1,4*lavoratori/50)`. Senza dati, indice contestualizzato assente. Gli zeri storici di esposizione sono adattati a dato assente.

Il target comune iniziale **4** proviene da `default_data` originale. Il referente non lo compila nella valutazione; solo l'amministratore lo cambia in Archivio e impostazioni. La politica include target/versione e resta nello snapshot. Un cambiamento invalida i calcoli temporanei precedenti e separa i confronti; non ricalcola lo storico.

## API e stato

`POST risk/calculate` e `risk/scenario`: validazione, cataloghi e calcolo temporaneo, nessuna scrittura delle valutazioni. `POST risk/save`: richiede hash del calcolo, ricalcola sul server, controlla politica/input e versione, salva esplicitamente con request_id idempotente. Non si fida di risultati inviati dal client. `risk/export` registra uno snapshot senza inserire la valutazione nello storico. `GET risk/history` mantiene l'ultima revisione Saved per cantiere/mese/modello, anche durante una bozza successiva. `GET risk/comparison` ammette soltanto mesi conclusi, stessa versione/target e cantieri autorizzati; espone le esclusioni. Tutte le revisioni restano disponibili.

L'hash comprende input adattati, politica, dati dichiarati, riferimenti e snapshot degli eventi. Modificare descrizioni, dati o fonti richiede ricalcolo. I risultati includono input originali/adattati, componenti grezze/effettive, bonus, limiti, soglia, motivazione, detection, assunzioni del contesto e sei scenari indipendenti dell'originale. I contributi non arrotondati riconciliano il risultato esatto; `score` a due decimali conserva l'output originale. Arrotondamento decimale con `sprintf`, verificato contro Python, per evitare la diversa gestione PHP dei quasi-mezzi.

## Evidenze e limiti

`python tests/model_parity.py`: 357 casi riproducibili con seed 2000, tutti i contributi, bisogni e motivazioni, bonus, soglie, contesti, avvisi, 2.142 scenari e confini delle fasce. Confronto numerico tolleranza assoluta 1e-8/relativa 1e-10. Test REST reali e browser verificano salvataggio, conflitti, persistenza ed export.

È equivalenza con il codice consegnato, non validazione predittiva o calibrazione scientifica. Nessun coefficiente nuovo. Le sole normalizzazioni legacy sono maiuscole/minuscole e `Scavo`→`scavi`; attività/temi sconosciuti bloccano il calcolo e richiedono scelta esplicita.
