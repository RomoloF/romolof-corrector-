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
import requests
import concurrent.futures

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

class RomoloApp:
    def __init__(self, root, selected_text):
        self.root = root
        self.root.title("Romolo AI Desktop")
        self.root.geometry("900x750")
        self.root.attributes('-topmost', True)
        self.config = load_config()
        self.variants = {}
        self.all_results = {} 
        self.current_lang = 'it'
        self.current_style = 'normal'
        self.original_text = selected_text
        self.model_status = {}
        self.last_quota_info = {"limit": "N/D", "remaining": "N/D", "reset": "N/D", "model": "N/D"}
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
        self.model_menu = ttk.Combobox(header, textvariable=self.model_var, values=self.config.get("available_models", []), width=25)
        self.model_menu.pack(side="left", padx=5)
        
        tk.Button(header, text="🚀 Trova Modello Libero", command=self.auto_find_working_model, bg="#34a853", fg="white", relief="flat").pack(side="left", padx=5)
        tk.Button(header, text="📋 Incolla", command=self.paste_from_clipboard, bg="#fbbc04", fg="black", relief="flat").pack(side="left", padx=5)
        tk.Button(header, text="🔄 Rigenera", command=self.regenerate_current, bg="#1a73e8", fg="white", relief="flat").pack(side="left", padx=5)
        tk.Button(header, text="🖥️ Terminale", command=self.run_terminal_fallback, bg="#6c757d", fg="white", relief="flat").pack(side="left", padx=5)

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

    def run_terminal_fallback(self):
        self.status_label.config(text="⏳ Avvio Motore Terminale...", fg="#6c757d")
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", "⏳ Utilizzo gemini-cli in corso...\nQuesta è l'ultima spiaggia.")
        
        def run():
            import subprocess
            # Prompt molto rigoroso per il terminale
            prompt = f"Agisci come Editor Senior. Riscrivi in 6 varianti JSON (it, en): normal, formal, technical, ironic, funny, debate. Testo: {self.original_text}. Restituisci SOLO il JSON puro senza commenti."
            try:
                # Esegue il comando da terminale chiamando 'gemini'
                result = subprocess.run(["gemini", prompt], capture_output=True, text=True, timeout=40)
                res_text = result.stdout
                
                if not res_text:
                    raise Exception("Il terminale non ha restituito alcun testo.")

                raw = re.sub(r'```json\s*|\s*```', '', res_text.strip())
                start, end = raw.find('{'), raw.rfind('}')
                if start == -1 or end == -1: raise Exception("Formato JSON non trovato nella risposta del terminale")
                
                res = json.loads(raw[start:end+1])
                self.variants = res
                self.all_results["Terminale"] = res
                self.model_status["Terminale"] = "ok"
                self.root.after(0, lambda: [self.model_var.set("Terminale"), self.set_style('normal'), self.status_label.config(text="✅ Risultato da Terminale", fg="green")])
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Errore Terminale", f"Non è stato possibile avviare o leggere gemini-cli:\n{e}\n\nAssicurati che sia installato correttamente."))
                self.root.after(0, lambda: self.status_label.config(text="❌ Errore Terminale", fg="red"))
        
        threading.Thread(target=run, daemon=True).start()

    def regenerate_current(self):
        m_name = self.model_var.get()
        self.status_label.config(text=f"⏳ Rigenerazione con {m_name}...", fg="#1a73e8")
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", f"⏳ Rigenerazione in corso con {m_name}...")
        threading.Thread(target=lambda: self.test_single_model(m_name), daemon=True).start()

    def paste_from_clipboard(self):
        try:
            txt = pyperclip.paste()
            if txt:
                self.original_text = txt
                self.start_analysis()
        except: pass

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
            self.text_area.insert(tk.END, "📡 MONITORAGGIO MODELLI E QUOTE\n", "title")
            self.text_area.insert(tk.END, "(Clicca su un modello per selezionarlo)\n", "subtitle")
            self.text_area.insert(tk.END, "------------------------------------------\n\n")
            
            for m_name, status in sorted(self.model_status.items()):
                icon = "🟢 FUNZIONANTE" if status == "ok" else "🔴 QUOTA ESAURITA" if status == "error" else "🔵 IN TEST..." if status == "testing" else "⚪ DISPONIBILE"
                color = "green" if status == "ok" else "red" if status == "error" else "blue" if status == "testing" else "gray"
                
                tag_name = f"model_{m_name}"
                self.text_area.insert(tk.END, f"{icon.ljust(18)} | ", color)
                self.text_area.insert(tk.END, f"{m_name}\n", tag_name)
                self.text_area.tag_configure(tag_name, foreground="#1a73e8", underline=True)
                self.text_area.tag_bind(tag_name, "<Button-1>", lambda e, n=m_name: self.select_model_manually(n))

            self.text_area.insert(tk.END, "\n\n📊 ANALISI TECNICA ULTIMA CHIAMATA\n", "title")
            self.text_area.insert(tk.END, "------------------------------------------\n")
            q = self.last_quota_info
            self.text_area.insert(tk.END, f"Modello: {q['model']}\n")
            self.text_area.insert(tk.END, f"Limite Totale (RPM): {q['limit']}\n")
            rem_color = "red" if str(q['remaining']) == "0" else "green"
            self.text_area.insert(tk.END, "Richieste Rimanenti: ", "bold")
            self.text_area.insert(tk.END, f"{q['remaining']}\n", rem_color)
            self.text_area.insert(tk.END, f"Reset Quota in: {q['reset']}\n")

            self.text_area.tag_configure("title", font=("Arial", 11, "bold"))
            self.text_area.tag_configure("subtitle", font=("Arial", 9, "italic"), foreground="#5f6368")
            self.text_area.tag_configure("bold", font=("Arial", 10, "bold"))
            self.text_area.tag_configure("green", foreground="#34a853")
            self.text_area.tag_configure("red", foreground="#ea4335", font=("Arial", 10, "bold"))
            self.text_area.tag_configure("blue", foreground="#1a73e8")
            self.text_area.tag_configure("gray", foreground="gray")
        elif self.variants:
            txt = self.variants.get(self.current_lang, {}).get(self.current_style, "")
            self.text_area.insert("1.0", txt)

    def select_model_manually(self, m_name):
        self.model_var.set(m_name)
        if m_name in self.all_results:
            self.variants = self.all_results[m_name]
            self.set_style('normal')
        else:
            self.regenerate_current()

    def start_analysis(self):
        self.variants = {}
        self.all_results = {}
        if self.current_style != 'models_list':
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", "⏳ Scansione rapida modelli in corso...")
        threading.Thread(target=self.run_parallel_scan, daemon=True).start()

    def run_parallel_scan(self):
        def get_models():
            combined = []
            pref = self.model_var.get()
            if pref: combined.append(pref)
            try:
                r = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={self.config['api_key']}", timeout=5)
                g_mods = [m['name'].replace('models/', '') for m in r.json().get('models', []) if 'generateContent' in m['supportedGenerationMethods']]
                g_mods.sort(key=lambda x: ("2.0" in x, "flash" in x), reverse=True)
                combined.extend(g_mods[:3])
            except: pass
            if self.config.get("deepseek_key"):
                try:
                    r = requests.get("https://openrouter.ai/api/v1/models", timeout=5)
                    ds_mods = [m['id'] for m in r.json().get('data', []) if ":free" in m.get('id', '')]
                    ds_mods.sort(key=lambda x: ("deepseek" in x or "llama-3.3" in x), reverse=True)
                    combined.extend(ds_mods[:5])
                except: pass
            res = []
            for m in combined:
                if m not in res:
                    res.append(m)
                    if m not in self.model_status: self.model_status[m] = "unknown"
            return res

        models = get_models()
        self.root.after(0, self.refresh_display)
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(self.test_single_model, models)
        self.root.after(0, lambda: self.status_label.config(text="🏁 Scansione rapida completata", fg="gray"))

    def test_single_model(self, m_name):
        self.model_status[m_name] = "testing"
        self.root.after(0, self.refresh_display)
        prompt = f"Riscrivi in 6 varianti JSON (it, en): normal, formal, technical, ironic, funny, debate. Testo: {self.original_text}"
        try:
            if "/" not in m_name:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m_name}:generateContent?key={self.config['api_key']}"
                resp = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=8)
                h = resp.headers
                self.last_quota_info = {"model": m_name, "limit": h.get('x-ratelimit-limit-requests', '15'), "remaining": h.get('x-ratelimit-remaining-requests', 'N/D'), "reset": h.get('x-ratelimit-reset-requests', 'N/D')}
                res_text = resp.json()['candidates'][0]['content']['parts'][0]['text']
            else:
                resp = requests.post(url="https://openrouter.ai/api/v1/chat/completions", headers={"Authorization": f"Bearer {self.config['deepseek_key']}", "X-Title": "Romolo AI"}, json={"model": m_name, "messages": [{"role": "user", "content": prompt}]}, timeout=10)
                h = resp.headers
                self.last_quota_info = {"model": m_name, "limit": 'Variabile (Free)', "remaining": 'Disponibile', "reset": 'N/D'}
                res_text = resp.json()['choices'][0]['message']['content']

            raw = re.sub(r'```json\s*|\s*```', '', res_text.strip())
            start, end = raw.find('{'), raw.rfind('}')
            res = json.loads(raw[start:end+1])
            self.all_results[m_name] = res
            self.model_status[m_name] = "ok"
            if not self.variants or self.model_var.get() == m_name:
                self.variants = res
                self.root.after(0, lambda: [self.model_var.set(m_name), self.set_style('normal')])
        except: self.model_status[m_name] = "error"
        self.root.after(0, self.refresh_display)

    def auto_find_working_model(self): self.start_analysis()
    def apply_action(self):
        text = self.text_area.get("1.0", tk.END).strip()
        with open(RESULT_FILE, "w", encoding="utf-8") as f: f.write(text)
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