# Registro Sessione Sviluppo Estensione "Romolo: Analizza e correggi"
**Data:** 30 Gennaio 2026
**Progetto:** Trasformazione di "Gemini Form Helper" in "Romolo AI Assistant"

---

## 1. Analisi Iniziale
**Stato di partenza:**
- Estensione semplice con API Key esposta nel codice (`background.js`).
- Sostituzione testo brutale (cancellava tutto il contenuto).
- Nessuna gestione errori.

**Richiesta Utente:** Mettere in sicurezza, migliorare la sostituzione, aggiungere gestione errori.

## 2. Implementazione Sicurezza e Opzioni
- **Azione:** Creazione di `options.html` e `options.js`.
- **Modifica:** Spostata la API Key dal codice allo `chrome.storage.sync`.
- **Fix:** Modificato `manifest.json` per rimuovere riferimenti a icone inesistenti che bloccavano il caricamento.

## 3. Risoluzione Problemi API e Modelli
- **Problema:** Errori 404 con modelli `v1beta` vs `v1`.
- **Problema:** Errore 429 (Quota Exceeded) con modelli sperimentali (`gemini-2.0-flash`).
- **Soluzione:** 
    - Creato pulsante **"Test Connessione"** nelle Opzioni.
    - Implementato recupero automatico della lista modelli disponibili per l'account utente.
    - Aggiunto test reale di generazione ("Ciao") per verificare se la quota è attiva o esaurita.

## 4. Evoluzione Funzionalità (Workflow)
### Fase A: Menu Contestuale Singolo
- Inizialmente un solo tasto "Correggi".

### Fase B: Stili Multipli
- Aggiunti sottomenu: *Normale, Formale, Tecnico*.
- Problema riscontrato: Chrome non aggiornava i menu.
- **Fix:** Aggiunto `chrome.contextMenus.removeAll()` all'avvio per pulire la cache dei menu.

### Fase C: Interfaccia Anteprima
- Invece di sostituire subito il testo, abbiamo creato un **Box Fluttuante**.
- L'utente può leggere la correzione prima di applicarla.

### Fase D: Multi-Variante Simultanea
- **Richiesta:** Vedere tutte le opzioni insieme.
- **Soluzione:** Prompt "JSON" che genera 3 versioni in una sola chiamata API.
- **UI:** Aggiunte schede (Tabs) nel box per cambiare stile istantaneamente.

## 5. Versione Finale "Romolo"
**Modifiche UI & UX:**
- Ingrandimento del box (600px) e dei font per leggibilità.
- Rinominato menu in **"Romolo: Analizza e correggi"**.

**Funzionalità Avanzate:**
1.  **Bilinguismo:** Aggiunto supporto **ITA / ENG**. Una singola analisi genera 6 varianti (3 ita + 3 eng).
2.  **Self-Correction:** Implementato prompt "Editor Senior" che obbliga l'AI a rileggere e correggere le bozze prima di inviarle (migliore qualità).

---

## Stato Finale dei File

### `manifest.json`
- Permessi: `storage`, `contextMenus`, `scripting`, `activeTab`.
- Pagina Opzioni configurata.

### `options.js`
- Gestisce salvataggio sicuro API Key.
- Test connessione intelligente (verifica reale della quota).
- Popolamento dinamico menu modelli.

### `background.js` (Il Cervello)
- **Prompt:** _"Agisci come Editor Senior... Fase 1 Drafting... Fase 2 Revisione... Restituisci JSON"_.
- **Gestione:** Parsa il JSON, inietta CSS e HTML nella pagina attiva.
- **UI:** Modale con Tab Stili (Normale/Formale/Tecnico) e Toggle Lingua (ITA/ENG).

---

## Istruzioni per l'uso
1. Selezionare testo in una pagina web.
2. Tasto Destro -> **Romolo: Analizza e correggi**.
3. Attendere il box.
4. Cliccare su **ENG** per le traduzioni o cambiare stile.
5. Premere **"Usa Questa"** per sostituire il testo originale.
