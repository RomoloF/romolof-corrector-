# 🚀 Guida all'Installazione: Romolo AI Suite

Benvenuto nella suite di Romolo AI. Questa guida ti aiuterà a configurare l'assistente su Chrome, LibreOffice e come applicazione Desktop.

---

## 1. 🔑 Configurazione delle Chiavi API (Essenziale)
Prima di iniziare, devi creare i file che conterranno le tue chiavi personali. Nella cartella principale del progetto, crea questi due file di testo:

1.  **`api_key.txt`**: Incolla qui la tua chiave Google Gemini (ottienila gratis su [Google AI Studio](https://aistudio.google.com/app/apikey)).
2.  **`api_key_deepseek.txt`**: Incolla qui la tua chiave OpenRouter per i modelli DeepSeek Free (ottienila su [OpenRouter.ai](https://openrouter.ai/)).

*Nota: Questi file sono ignorati da Git e rimarranno sicuri sul tuo computer.*

---

## 2. 🌐 Estensione per Google Chrome
L'estensione permette di analizzare il testo selezionato su qualsiasi sito web.

1.  Apri Chrome e vai all'indirizzo: `chrome://extensions/`
2.  Attiva la **"Modalità sviluppatore"** in alto a destra.
3.  Clicca su **"Carica estensione non impacchettata"**.
4.  Seleziona la cartella principale del progetto (`gemini-corrector`).
5.  Clicca sull'icona dell'estensione nella barra di Chrome -> **Opzioni** e verifica che la tua API Key sia salvata.

---

## 3. 🖥️ Applicazione Desktop (Python)
L'app desktop offre la scansione parallela turbo e il monitoraggio tecnico delle quote.

### Requisiti
Assicurati di avere Python installato. Installa le librerie necessarie con questo comando:
```bash
pip install google-generativeai pyperclip requests
sudo apt install python3-tk  # Necessario solo su sistemi Linux (Ubuntu/Debian)
```

### Avvio
Per lanciare l'applicazione:
```bash
python3 romolo_desktop.py
```

---

## 4. 📝 Integrazione LibreOffice Writer
Aggiunge un pulsante "Romolo AI" direttamente nella barra degli strumenti di Writer.

1.  Copia il file `romolo_writer.py` nella cartella delle macro di LibreOffice:
    ```bash
    mkdir -p ~/.config/libreoffice/4/user/Scripts/python/
    cp romolo_writer.py ~/.config/libreoffice/4/user/Scripts/python/
    ```
2.  Esegui lo script di installazione del pulsante:
    ```bash
    python3 install_writer_button.py
    ```
3.  Riavvia LibreOffice Writer. Troverai il pulsante nella barra delle funzioni standard.

---

## 🛰️ Funzionalità Avanzate
-   **Scansione Parallela**: L'app interroga 10 modelli contemporaneamente per garantirti un risultato istantaneo.
-   **Stato Modelli**: La tab "📡 STATO MODELLI" mostra quali IA sono attive e quante richieste ti rimangono (RPM/RPD).
-   **Terminal Fallback**: Se le API cloud sono sature, il pulsante "🖥️ Terminale" usa il comando locale `gemini` del tuo sistema.

---
*Sviluppato con passione per rendere l'IA accessibile e indistruttibile.*
