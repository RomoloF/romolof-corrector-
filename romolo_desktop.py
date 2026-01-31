#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import google.generativeai as genai
import pyperclip
import json
import threading
import sys
import os
import time
import warnings
import re

warnings.filterwarnings("ignore", category=FutureWarning)

CONFIG_FILE = "/home/romolo/Scrivania/gemini-corrector/config.json"
INPUT_FILE = "/tmp/romolo_input.txt"
RESULT_FILE = "/tmp/romolo_result.txt"

def load_config():
    defaults = {"api_key": "", "model": "gemini-1.5-flash", "available_models": ["gemini-1.5-flash", "gemini-pro-latest"]}
    path_key = "/home/romolo/Scrivania/gemini-corrector/api_key.txt"
    if os.path.exists(path_key):
        with open(path_key, "r") as f:
            defaults["api_key"] = f.read().strip()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return {**defaults, **json.load(f)}
        except: pass
    return defaults

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

class RomoloApp:
    def __init__(self, root, selected_text):
        self.root = root
        self.root.title("Romolo AI Desktop")
        self.root.geometry("800x650")
        self.root.attributes('-topmost', True)
        self.config = load_config()
        self.variants = {}
        self.current_lang = 'it'
        self.current_style = 'normal'
        self.original_text = selected_text
        self.setup_ui()
        if self.config["api_key"]:
            self.start_analysis()
        else:
            self.text_area.insert("1.0", "⚠️ API Key mancante! Controlla api_key.txt")

    def setup_ui(self):
        header = tk.Frame(self.root, bg="#f1f3f4", pady=10)
        header.pack(fill="x")
        tk.Label(header, text="Romolo AI", font=("Arial", 14, "bold"), bg="#f1f3f4", fg="#1a73e8").pack(side="left", padx=20)
        
        self.model_var = tk.StringVar(value=self.config["model"])
        self.model_menu = ttk.Combobox(header, textvariable=self.model_var, values=self.config["available_models"], width=25)
        self.model_menu.pack(side="left", padx=5)
        
        tk.Button(header, text="🚀 Trova Modello", command=self.auto_find_working_model, bg="#34a853", fg="white", relief="flat").pack(side="left", padx=5)
        
        # Nuovo tasto Incolla
        tk.Button(header, text="📋 Incolla", command=self.paste_from_clipboard, bg="#fbbc04", fg="black", relief="flat").pack(side="left", padx=5)

        lang_frame = tk.Frame(header, bg="#f1f3f4")
        lang_frame.pack(side="right", padx=20)
        self.btn_it = tk.Button(lang_frame, text="🇮🇹 ITA", command=lambda: self.set_lang('it'), relief="flat", bg="#d2e3fc")
        self.btn_it.pack(side="left", padx=2)
        self.btn_en = tk.Button(lang_frame, text="🇬🇧 ENG", command=lambda: self.set_lang('en'), relief="flat", bg="white")
        self.btn_en.pack(side="left", padx=2)

        tab_frame = tk.Frame(self.root, bg="#dee2e6")
        tab_frame.pack(fill="x")
        self.tabs = {}
        for s_id, label in [('normal', 'Normale'), ('formal', 'Formale'), ('technical', 'Tecnico')]:
            btn = tk.Button(tab_frame, text=label, command=lambda s=s_id: self.set_style(s), relief="flat")
            btn.pack(side="left", expand=True, fill="x")
            self.tabs[s_id] = btn

        self.text_area = tk.Text(self.root, font=("Arial", 13), wrap="word", padx=15, pady=15)
        self.text_area.pack(fill="both", expand=True)
        
        footer = tk.Frame(self.root, pady=10, padx=20)
        footer.pack(fill="x")
        self.status_label = tk.Label(footer, text="Pronto", fg="#5f6368")
        self.status_label.pack(side="left")
        tk.Button(footer, text="Usa Questa (Sostituisci)", command=self.apply_action, bg="#1a73e8", fg="white", font=("Arial", 10, "bold"), width=25).pack(side="right")

    def paste_from_clipboard(self):
        txt = pyperclip.paste()
        if txt:
            self.original_text = txt
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", txt)
            self.start_analysis()

    def set_lang(self, lang):
        self.current_lang = lang
        self.btn_it.config(bg="#d2e3fc" if lang == 'it' else "white")
        self.btn_en.config(bg="#d2e3fc" if lang == 'en' else "white")
        self.refresh_display()

    def set_style(self, style):
        self.current_style = style
        for s_id, btn in self.tabs.items():
            btn.config(bg="white" if s_id == style else "#e8eaed", font=("Arial", 10, "bold" if s_id == style else "normal"))
        self.refresh_display()

    def refresh_display(self):
        if self.variants:
            txt = self.variants.get(self.current_lang, {}).get(self.current_style, "")
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", txt)

    def start_analysis(self):
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", f"⏳ Analizzando con {self.model_var.get()}...")
        threading.Thread(target=self.analyze_text, args=(self.original_text,), daemon=True).start()

    def analyze_text(self, text):
        prompt = f"""
          Agisci come Editor Senior. Riscrivi il testo con Self-Correction.
          Output richiesto: JSON con chiavi "it" e "en", ognuna con "normal", "formal", "technical".
          Testo: "{text}"
          Restituisci SOLO il JSON puro.
        """
        try:
            genai.configure(api_key=self.config["api_key"])
            model = genai.GenerativeModel(self.model_var.get())
            response = model.generate_content(prompt)
            
            if not response.text:
                raise Exception("L'AI ha risposto con un testo vuoto (possibile blocco sicurezza).")

            # Pulizia avanzata del JSON
            raw = response.text.strip()
            # Rimuove blocchi markdown ```json ... ```
            raw = re.sub(r'```json\s*|\s*```', '', raw)
            # Cerca il primo { e l'ultimo }
            start = raw.find('{')
            end = raw.rfind('}')
            if start != -1 and end != -1:
                raw = raw[start:end+1]
            
            self.variants = json.loads(raw)
            self.root.after(0, lambda: self.set_style('normal'))
            self.root.after(0, lambda: self.status_label.config(text="✅ Analisi completata", fg="green"))
        except Exception as e:
            err = str(e)
            self.root.after(0, lambda: self.status_label.config(text="❌ Errore", fg="red"))
            self.root.after(0, lambda: self.text_area.delete("1.0", tk.END))
            self.root.after(0, lambda: self.text_area.insert("1.0", f"ERRORE ANALISI:\n{err}\n\nRisposta AI:\n{response.text if 'response' in locals() else 'Nessuna'}"))

    def auto_find_working_model(self):
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", "🚀 Ricerca modello libero...")
        def run():
            try:
                genai.configure(api_key=self.config["api_key"])
                models = [m.name.replace('models/', '') for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                for m_name in models:
                    try:
                        genai.GenerativeModel(m_name).generate_content("test")
                        self.config["model"] = m_name
                        save_config(self.config)
                        self.root.after(0, lambda n=m_name: self.model_var.set(n))
                        self.root.after(0, self.start_analysis)
                        return
                    except: continue
                self.root.after(0, lambda: messagebox.showerror("Errore", "Nessun modello libero."))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Errore", str(e)))
        threading.Thread(target=run, daemon=True).start()

    def apply_action(self):
        text = self.text_area.get("1.0", tk.END).strip()
        with open(RESULT_FILE, "w", encoding="utf-8") as f:
            f.write(text)
        self.root.destroy()

if __name__ == "__main__":
    txt = ""
    # 1. Controllo se arriva da LibreOffice
    if os.path.exists(INPUT_FILE):
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            txt = f.read()
        os.remove(INPUT_FILE)
    # 2. Controllo argomenti riga di comando
    elif len(sys.argv) > 1:
        txt = sys.argv[1]
    # 3. Controllo Appunti
    else:
        try:
            clipboard_content = pyperclip.paste()
            if clipboard_content and len(clipboard_content.strip()) > 5:
                txt = clipboard_content
        except:
            pass
    
    if not txt: txt = "Scrivi o incolla qui il testo da analizzare..."
    
    root = tk.Tk()
    app = RomoloApp(root, txt)
    root.mainloop()