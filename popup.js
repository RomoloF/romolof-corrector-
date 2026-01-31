document.addEventListener('DOMContentLoaded', async () => {
  const statusDot = document.getElementById('statusDot');
  const statusText = document.getElementById('statusText');
  const modelSelect = document.getElementById('modelQuickSelect');
  const openOptions = document.getElementById('openOptions');
  const testBtn = document.getElementById('testBtn');

  // 1. Carica stato iniziale
  const config = await chrome.storage.sync.get(['geminiApiKey', 'geminiModel']);
  
  if (config.geminiApiKey) {
    statusDot.classList.add('ok');
    statusText.textContent = 'API Key Configurata';
  } else {
    statusDot.classList.add('error');
    statusText.textContent = 'API Key Mancante';
    statusText.style.color = '#ea4335';
  }

  if (config.geminiModel) {
    modelSelect.value = config.geminiModel;
  }

  // 2. Salva modello al cambio rapido
  modelSelect.addEventListener('change', () => {
    chrome.storage.sync.set({ geminiModel: modelSelect.value }, () => {
      // Feedback visivo rapido
      const originalText = statusText.textContent;
      statusText.textContent = 'Modello aggiornato!';
      setTimeout(() => statusText.textContent = originalText, 1500);
    });
  });

  // 3. Apri Opzioni
  openOptions.addEventListener('click', () => {
    chrome.runtime.openOptionsPage();
  });

  // 4. Test rapido
  testBtn.addEventListener('click', async () => {
    testBtn.disabled = true;
    testBtn.textContent = '...';
    
    const { geminiApiKey, geminiModel } = await chrome.storage.sync.get(['geminiApiKey', 'geminiModel']);
    const model = geminiModel || 'gemini-2.0-flash';

    try {
      const resp = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${geminiApiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contents: [{ parts: [{ text: "hi" }] }] })
      });
      
      if (resp.ok) {
        statusText.textContent = 'Connessione OK! ✅';
        statusText.style.color = '#34a853';
      } else {
        throw new Error();
      }
    } catch (e) {
      statusText.textContent = 'Errore Connessione ❌';
      statusText.style.color = '#ea4335';
    } finally {
      setTimeout(() => {
        statusText.textContent = geminiApiKey ? 'API Key Configurata' : 'API Key Mancante';
        statusText.style.color = '';
        testBtn.disabled = false;
        testBtn.textContent = '⚡ Test';
      }, 2000);
    }
  });
});