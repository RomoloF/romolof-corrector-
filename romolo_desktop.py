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
    defaults = {"api_key": "", "deepseek_key": "", "model": "gemini-2.0-flash", "available_models": []}
    path_key = "/home/romolo/Scrivania/gemini-corrector/api_key.txt"
    path_ds = "/home/romolo/Scrivania/gemini-corrector/api_key_deepseek.txt"
    if os.path.exists(path_key):
        with open(path_key, "r") as f: defaults["api_key"] = f.read().strip()
    if os.path.exists(path_ds):
        with open(path_ds, "r") as f: defaults["deepseek_key"] = f.read().strip()
    return defaults

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

class RomoloApp:
    def __init__(self, root, selected_text):
        self.root = root
        self.root.title("Romolo AI Desktop")
        self.root.geometry("900x700")
        self.root.attributes('-topmost', True)
        self.config = load_config()
        self.variants = {}
        self.all_results = {} # Memorizza i risultati per ogni modello: {nome_modello: varianti}
        self.current_lang = 'it'
        self.current_style = 'normal'
        self.original_text = selected_text
        self.model_status = {}
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
        
        tk.Button(header, text="🚀 Trova Modello Libero", command=self.auto_find_working_model, bg="#34a853", fg="white", relief="flat").pack(side="left", padx=5)
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
        modalita = [
            ('normal', 'Normale'), ('formal', 'Formale'), ('technical', 'Tecnico'),
            ('ironic', 'Ironico'), ('funny', 'Comico'), ('debate', 'Critico'),
            ('models_list', '📡 STATO MODELLI')
        ]
        for s_id, label in modalita:
            btn = tk.Button(tab_frame, text=label, command=lambda s=s_id: self.set_style(s), relief="flat")
            if s_id == 'models_list': btn.config(bg="#e8f0fe", fg="#1a73e8")
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
            self.start_analysis()

    def set_lang(self, lang):
        self.current_lang = lang
        self.btn_it.config(bg="#d2e3fc" if lang == 'it' else "white")
        self.btn_en.config(bg="#d2e3fc" if lang == 'en' else "white")
        self.refresh_display()

    def set_style(self, style):
        self.current_style = style
        for s_id, btn in self.tabs.items():
            is_active = (s_id == style)
            btn.config(bg="white" if is_active else "#e8eaed", font=("Arial", 10, "bold" if is_active else "normal"))
        self.refresh_display()

    def refresh_display(self):
        self.text_area.delete("1.0", tk.END)
        if self.current_style == 'models_list':
            self.text_area.insert(tk.END, "📡 MONITORAGGIO MODELLI GEMINI\n", "title")
            self.text_area.insert(tk.END, "(Clicca su un modello per forzarne l'uso)\n", "subtitle")
            self.text_area.insert(tk.END, "------------------------------------------\n\n")
            
            for m_name, status in sorted(self.model_status.items()):
                if status == "ok":
                    icon, color = "🟢 FUNZIONANTE", "green"
                elif status == "error":
                    icon, color = "🔴 QUOTA ESAURITA", "red"
                elif status == "testing":
                    icon, color = "🔵 IN TEST...", "blue"
                else:
                    icon, color = "⚪ DISPONIBILE", "gray"
                
                tag_name = f"model_{m_name}"
                self.text_area.insert(tk.END, f"{icon.ljust(18)} | ", color)
                self.text_area.insert(tk.END, f"{m_name}\n", tag_name)
                
                self.text_area.tag_configure(tag_name, foreground="#1a73e8", underline=True)
                self.text_area.tag_bind(tag_name, "<Button-1>", lambda e, n=m_name: self.select_model_manually(n))
                self.text_area.tag_bind(tag_name, "<Enter>", lambda e: self.text_area.config(cursor="hand2"))
                self.text_area.tag_bind(tag_name, "<Leave>", lambda e: self.text_area.config(cursor=""))

            self.text_area.tag_configure("title", font=("Arial", 12, "bold"))
            self.text_area.tag_configure("subtitle", font=("Arial", 9, "italic"), foreground="#5f6368")
            self.text_area.tag_configure("green", foreground="#34a853")
            self.text_area.tag_configure("red", foreground="#ea4335")
            self.text_area.tag_configure("blue", foreground="#1a73e8")
            self.text_area.tag_configure("gray", foreground="gray")
        elif self.variants:
            txt = self.variants.get(self.current_lang, {}).get(self.current_style, "")
            self.text_area.insert("1.0", txt)

    def select_model_manually(self, m_name):
        self.model_var.set(m_name)
        # Se abbiamo già il risultato per questo modello, caricalo subito
        if m_name in self.all_results:
            self.variants = self.all_results[m_name]
            self.status_label.config(text=f"✅ Visualizzando: {m_name}", fg="green")
            self.set_style('normal')
        else:
            self.status_label.config(text=f"⏳ Analisi singola: {m_name}", fg="blue")
            self.start_analysis()

    def start_analysis(self):
        if self.current_style != 'models_list':
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", "⏳ Ricerca modelli e analisi in corso...")
        threading.Thread(target=self.analyze_text, args=(self.original_text,), daemon=True).start()

    def analyze_text(self, text):
        # Modelli da testare: Gemini + DeepSeek Free
        gemini_models = []
        try:
            genai.configure(api_key=self.config["api_key"])
            gemini_models = [m.name.replace('models/', '') for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            gemini_models.sort(key=lambda x: ("2.0" in x, "1.5" in x), reverse=True)
        except: pass

        ds_models = ["deepseek/deepseek-r1:free", "deepseek/deepseek-chat:free", "google/gemini-2.0-flash-exp:free"]
        
        all_models = gemini_models + ds_models
        for m in all_models: 
            if m not in self.model_status: self.model_status[m] = "unknown"

        def attempt(models, idx):
            if idx >= len(models):
                self.root.after(0, lambda: self.status_label.config(text="🏁 Scansione completata", fg="gray"))
                return

            m_name = models[idx]
            self.model_status[m_name] = "testing"
            self.root.after(0, self.refresh_display)

            prompt = f"Riscrivi in 6 varianti JSON (it, en): normal, formal, technical, ironic, funny, debate. Testo: {text}"
            
            try:
                # LOGICA GEMINI
                if "/" not in m_name:
                    model = genai.GenerativeModel(m_name)
                    response = model.generate_content(prompt)
                    res_text = response.text
                # LOGICA DEEPSEEK (OpenRouter)
                else:
                    if not self.config["deepseek_key"]: raise Exception("No DS Key")
                    import requests
                    resp = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completations",
                        headers={"Authorization": f"Bearer {self.config['deepseek_key']}"},
                        data=json.dumps({
                            "model": m_name,
                            "messages": [{"role": "user", "content": prompt}]
                        })
                    )
                    res_text = resp.json()['choices'][0]['message']['content']

                raw = re.sub(r'```json\s*|\s*```', '', res_text.strip())
                start, end = raw.find('{'), raw.rfind('}')
                res = json.loads(raw[start:end+1])
                
                self.all_results[m_name] = res
                self.model_status[m_name] = "ok"
                if not self.variants:
                    self.variants = res
                    self.root.after(0, lambda: [self.model_var.set(m_name), self.set_style('normal')])
                
                self.root.after(0, self.refresh_display)
                attempt(models, idx + 1)

            except Exception as e:
                self.model_status[m_name] = "error"
                self.root.after(0, self.refresh_display)
                attempt(models, idx + 1)

        threading.Thread(target=lambda: attempt(all_models, 0), daemon=True).start()

    def auto_find_working_model(self):
        self.start_analysis()

    def apply_action(self):
        text = self.text_area.get("1.0", tk.END).strip()
        with open(RESULT_FILE, "w", encoding="utf-8") as f:
            f.write(text)
        self.root.destroy()

if __name__ == "__main__":
    txt = ""
    if os.path.exists(INPUT_FILE):
        with open(INPUT_FILE, "r", encoding="utf-8") as f: txt = f.read()
        os.remove(INPUT_FILE)
    else:
        try:
            c = pyperclip.paste()
            if c and len(c.strip()) > 5: txt = c
        except: pass
    if not txt: txt = "Scrivi o incolla qui il testo..."
    root = tk.Tk()
    app = RomoloApp(root, txt)
    root.mainloop()
