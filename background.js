// background.js - Versione Robusta

// Inizializzazione Menu
const createMenu = () => {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({
      id: "gemini-analyze",
      title: "Romolo: Analizza e correggi",
      contexts: ["selection"]
    });
  });
};

chrome.runtime.onInstalled.addListener(createMenu);
chrome.runtime.onStartup.addListener(createMenu);

// Gestione click menu
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === "gemini-analyze") {
    const selectedText = info.selectionText;

    // 1. Controllo immediato URL protetti
    if (!tab.url || tab.url.startsWith('chrome://') || tab.url.startsWith('edge://') || tab.url.startsWith('about:')) {
      notifyUser("Errore", "L'estensione non può funzionare sulle pagine di sistema di Chrome.");
      return;
    }

    try {
      // 2. Recupero impostazioni con await (più pulito)
      const result = await chrome.storage.sync.get(['geminiApiKey', 'geminiModel']);
      const apiKey = result.geminiApiKey;
      const model = result.geminiModel || 'gemini-2.0-flash';

      if (!apiKey) {
        notifyUser("Configurazione Mancante", "API Key non trovata. Vai nelle opzioni dell'estensione.");
        return;
      }
      
      // 3. Cursore wait (con catch per evitare crash)
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => document.body.style.cursor = 'wait'
      }).catch(() => {});

      console.log("Richiesta inviata a:", model);

      const prompt = `
        Agisci come un Editor Senior. Analizza il testo e produci versioni perfezionate.
        Restituisci ESCLUSIVAMENTE un oggetto JSON valido:
        {
          "it": { "normal": "...", "formal": "...", "technical": "..." },
          "en": { "normal": "...", "formal": "...", "technical": "..." }
        }
        Testo: "${selectedText}"
      `;

      const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }] })
      });

      if (!response.ok) {
         const err = await response.json().catch(() => ({}));
         throw new Error(err.error?.message || "Errore API Google");
      }

      const data = await response.json();
      const rawText = data.candidates[0].content.parts[0].text;
      
      // Estrazione JSON robusta
      const jsonMatch = rawText.match(/\{[\s\S]*\}/);
      if (!jsonMatch) throw new Error("Risposta AI non valida.");
      
      const variants = JSON.parse(jsonMatch[0]);

      // 4. Iniezione Modale
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: showComparisonModal,
        args: [variants]
      });

    } catch (error) {
      console.error("Errore Romolo:", error);
      notifyUser("Errore Romolo", error.message);
    } finally {
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => document.body.style.cursor = 'default'
      }).catch(() => {});
    }
  }
});

// Funzione di notifica nativa (funziona ovunque)
function notifyUser(title, message) {
  chrome.notifications.create({
    type: "basic",
    iconUrl: "icon.png",
    title: title,
    message: message,
    priority: 2
  });
}

// --- UI INIETTATA ---
function showComparisonModal(variants) {
  const existingModal = document.getElementById('gemini-comparison-box');
  if (existingModal) existingModal.remove();

  const activeElement = document.activeElement;

  const css = `
    #gemini-comparison-box {
      position: fixed; top: 20px; right: 20px; width: 550px;
      background: #fff; border: 1px solid #ccc; box-shadow: 0 8px 30px rgba(0,0,0,0.3);
      z-index: 2147483647; font-family: sans-serif; border-radius: 12px; overflow: hidden;
      display: flex; flex-direction: column; color: #333;
    }
    .g-header { background: #f8f9fa; padding: 12px; border-bottom: 1px solid #ddd; display: flex; justify-content: space-between; align-items: center; }
    .g-title { font-weight: bold; color: #1a73e8; }
    .g-lang-toggle { display: flex; gap: 5px; }
    .g-lang-btn { border: 1px solid #ddd; background: #fff; padding: 4px 8px; cursor: pointer; border-radius: 4px; font-size: 12px; }
    .g-lang-btn.active { background: #1a73e8; color: #fff; border-color: #1a73e8; }
    .g-close { border: none; background: none; font-size: 20px; cursor: pointer; }
    .g-tabs { display: flex; background: #eee; }
    .g-tab { flex: 1; padding: 10px; border: none; background: none; cursor: pointer; border-bottom: 2px solid transparent; }
    .g-tab.active { background: #fff; border-bottom: 2px solid #1a73e8; font-weight: bold; }
    .g-content { padding: 15px; }
    .g-textarea { width: 100%; height: 250px; margin-bottom: 10px; padding: 10px; box-sizing: border-box; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; resize: none; }
    .g-actions { display: flex; gap: 10px; }
    .g-btn { flex: 1; padding: 10px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
    .g-btn-p { background: #1a73e8; color: #fff; }
    .g-btn-s { background: #eee; }
  `;

  const style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);

  const modal = document.createElement('div');
  modal.id = 'gemini-comparison-box';
  modal.innerHTML = `
    <div class="g-header">
      <span class="g-title">Romolo AI</span>
      <div class="g-lang-toggle">
        <button class="g-lang-btn active" id="btn-it">🇮🇹 ITA</button>
        <button class="g-lang-btn" id="btn-en">🇬🇧 ENG</button>
      </div>
      <button class="g-close">&times;</button>
    </div>
    <div class="g-tabs">
      <button class="g-tab active" data-s="normal">Normale</button>
      <button class="g-tab" data-s="formal">Formale</button>
      <button class="g-tab" data-s="technical">Tecnico</button>
    </div>
    <div class="g-content">
      <textarea class="g-textarea" id="g-text"></textarea>
      <div class="g-actions">
        <button class="g-btn g-btn-p" id="g-apply">Applica</button>
        <button class="g-btn g-btn-s" id="g-copy">Copia</button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);

  let lang = 'it';
  let style_id = 'normal';
  const area = modal.querySelector('#g-text');

  const update = () => { area.value = variants[lang][style_id] || ""; };
  update();

  modal.querySelector('#btn-it').onclick = () => { lang = 'it'; modal.querySelector('#btn-it').classList.add('active'); modal.querySelector('#btn-en').classList.remove('active'); update(); };
  modal.querySelector('#btn-en').onclick = () => { lang = 'en'; modal.querySelector('#btn-en').classList.add('active'); modal.querySelector('#btn-it').classList.remove('active'); update(); };
  
  modal.querySelectorAll('.g-tab').forEach(t => {
    t.onclick = () => {
      modal.querySelectorAll('.g-tab').forEach(x => x.classList.remove('active'));
      t.classList.add('active');
      style_id = t.getAttribute('data-s');
      update();
    };
  });

  modal.querySelector('.g-close').onclick = () => modal.remove();
  modal.querySelector('#g-copy').onclick = () => {
    navigator.clipboard.writeText(area.value);
    modal.querySelector('#g-copy').textContent = "Copiato!";
    setTimeout(() => modal.querySelector('#g-copy').textContent = "Copia", 1000);
  };

  modal.querySelector('#g-apply').onclick = () => {
    if (activeElement && (activeElement.tagName === "TEXTAREA" || activeElement.tagName === "INPUT")) {
      const s = activeElement.selectionStart;
      const e = activeElement.selectionEnd;
      activeElement.setRangeText(area.value, s, e, 'select');
    } else {
      navigator.clipboard.writeText(area.value);
    }
    modal.remove();
  };
}
