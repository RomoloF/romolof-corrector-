# Romolo AI - Suite di Correzione Intelligente

Romolo AI è un assistente alla scrittura avanzato basato su Google Gemini. Offre correzione grammaticale, miglioramento dello stile e traduzione idiomatica in un'unica soluzione integrata.

## 🚀 Caratteristiche
- **Chrome Extension**: Analizza il testo selezionato in qualsiasi sito web tramite menu contestuale.
- **Interfaccia Multi-Variante**: Scegli tra tono Normale, Formale o Tecnico in Italiano e Inglese.
- **LibreOffice Integration**: Un pulsante dedicato direttamente dentro Writer per correggere i tuoi documenti.
- **Desktop App**: Interfaccia standalone in Python (Tkinter) per un'esperienza fluida.

## 🛠 Installazione

### Estensione Chrome
1. Carica la cartella in `chrome://extensions/` in modalità sviluppatore.
2. Configura la tua API Key nelle opzioni.

### LibreOffice & Desktop
1. Installa le dipendenze: `pip install google-generativeai pyperclip`
2. Esegui `python3 install_writer_button.py` per aggiungere il pulsante a Writer.

## 🔑 Configurazione
Crea un file `api_key.txt` nella root del progetto e incolla la tua chiave ottenuta da [Google AI Studio](https://aistudio.google.com/app/apikey).

---
*Sviluppato con ❤️ per migliorare la scrittura quotidiana.*
