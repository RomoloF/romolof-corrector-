// Funzione helper per mostrare messaggi
const showStatus = (msg, color = 'black') => {
  const status = document.getElementById('status');
  status.style.color = color;
  status.textContent = msg;
  setTimeout(() => { status.textContent = ''; }, 4000);
};

// Salva la chiave e il modello nello storage di Chrome
const saveOptions = () => {
  const apiKey = document.getElementById('apiKey').value;
  const model = document.getElementById('modelSelect').value;
  
  if (!apiKey) {
    showStatus('Errore: Inserisci una API Key prima di salvare.', 'red');
    return;
  }

  chrome.storage.sync.set({
    geminiApiKey: apiKey,
    geminiModel: model 
  }, () => {
    showStatus('✅ Opzioni salvate correttamente!', 'green');
  });
};

// Ripristina lo stato salvato all'apertura
const restoreOptions = () => {
  chrome.storage.sync.get({ geminiApiKey: '', geminiModel: 'gemini-2.0-flash' }, (items) => {
    if (items.geminiApiKey) {
      document.getElementById('apiKey').value = items.geminiApiKey;
    }
    if (items.geminiModel) {
      document.getElementById('modelSelect').value = items.geminiModel;
    }
  });
};

// Test della connessione, verifica quota e aggiorna lista modelli
const testConnection = async () => {
  const apiKey = document.getElementById('apiKey').value;
  const debugDiv = document.getElementById('debugOutput');
  const quotaStatus = document.getElementById('quotaStatus');
  const quotaMessage = document.getElementById('quotaMessage');
  
  if (!apiKey) {
    showStatus('Inserisci prima una API Key!', 'red');
    return;
  }

  debugDiv.style.display = 'block';
  debugDiv.textContent = 'Verifica in corso...';
  quotaStatus.style.display = 'none';

  try {
    // 1. Scarica la lista modelli
    const listResponse = await fetch(`https://generativelanguage.googleapis.com/v1beta/models?key=${apiKey}`);
    const listData = await listResponse.json();

    if (!listResponse.ok) throw new Error(listData.error?.message || listResponse.statusText);

    // 2. Aggiorna il menu a tendina con i modelli reali
    if (listData.models) {
      const availableModels = listData.models
        .filter(m => m.supportedGenerationMethods && m.supportedGenerationMethods.includes('generateContent'))
        .map(m => m.name.replace('models/', ''))
        .sort();

      const select = document.getElementById('modelSelect');
      const previousSelection = select.value;
      
      select.innerHTML = ''; // Pulisci
      
      availableModels.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m;
        opt.textContent = m;
        select.appendChild(opt);
      });

      // Ripristina selezione o metti default intelligente
      if (availableModels.includes(previousSelection)) {
        select.value = previousSelection;
      } else {
        const bestDefault = availableModels.find(m => m.includes('1.5-flash')) || availableModels[0];
        select.value = bestDefault;
      }
      
      debugDiv.textContent = `✅ Lista modelli aggiornata (${availableModels.length} modelli trovati).\n`;
    }

    // 3. TEST REALE DI QUOTA (Prova a generare 'Ciao')
    const modelToTest = document.getElementById('modelSelect').value;
    debugDiv.textContent += `Testing generazione con: ${modelToTest}...
`;

    const genResponse = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${modelToTest}:generateContent?key=${apiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contents: [{ parts: [{ text: "Ciao" }] }] })
    });

    if (genResponse.status === 429) {
      quotaStatus.style.display = 'block';
      quotaStatus.style.background = '#f8d7da';
      quotaStatus.style.color = '#721c24'; // Rosso scuro
      quotaMessage.textContent = `QUOTA ESAURITA per ${modelToTest}. Cambia modello e riprova il test.`;
      debugDiv.textContent += "❌ ERRORE 429: Quota esaurita.";
    } else if (!genResponse.ok) {
      const err = await genResponse.json();
      throw new Error(`Errore Generazione: ${err.error?.message}`);
    } else {
      // SUCCESSO TOTALE
      quotaStatus.style.display = 'block';
      quotaStatus.style.background = '#d4edda';
      quotaStatus.style.color = '#155724'; // Verde scuro
      quotaMessage.textContent = "✅ Quota OK! Tutto funzionante.";
      debugDiv.textContent += "✅ Generazione riuscita! Puoi salvare.";
      
      // Auto-salvataggio opzionale per comodità
      // saveOptions(); // Meglio lasciarlo manuale per evitare confusione
      showStatus("Test superato! Clicca SALVA per confermare.", "blue");
    }

  } catch (error) {
    debugDiv.textContent += '\n❌ ERRORE:\n' + error.message;
  }
};

document.addEventListener('DOMContentLoaded', restoreOptions);
document.getElementById('save').addEventListener('click', saveOptions);
document.getElementById('testConnection').addEventListener('click', testConnection);