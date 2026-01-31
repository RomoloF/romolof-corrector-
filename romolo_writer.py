import uno
import subprocess
import os
import time

def RomoloAnalizza():
    """Versione 3.0 - Integrazione Totale"""
    try:
        ctx = uno.getComponentContext()
        smgr = ctx.ServiceManager
        desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        doc = desktop.getCurrentComponent()
        
        selection = doc.getCurrentSelection()
        if not selection: return
        range_obj = selection.getByIndex(0)
        selected_text = range_obj.getString()
        if not selected_text.strip(): return

        # File di scambio
        input_file = "/tmp/romolo_input.txt"
        result_file = "/tmp/romolo_result.txt"
        
        with open(input_file, "w", encoding="utf-8") as f:
            f.write(selected_text)
        
        if os.path.exists(result_file):
            os.remove(result_file)

        # Lancio Romolo Desktop
        script_path = "/home/romolo/Scrivania/gemini-corrector/romolo_desktop.py"
        my_env = os.environ.copy()
        if "DISPLAY" not in my_env: my_env["DISPLAY"] = ":0"
        
        # Lanciamo e non aspettiamo il processo, ma aspettiamo il FILE
        subprocess.Popen(["python3", script_path], env=my_env)
        
        # Aspettiamo il file per 5 minuti
        start_time = time.time()
        while time.time() - start_time < 300:
            if os.path.exists(result_file):
                time.sleep(0.2)
                with open(result_file, "r", encoding="utf-8") as f:
                    new_text = f.read()
                
                # Sostituzione reale nel documento
                range_obj.setString(new_text)
                os.remove(result_file)
                break
            time.sleep(0.5)
            
    except Exception as e:
        with open("/tmp/romolo_error.log", "w") as f:
            f.write(str(e))

g_exportedScripts = (RomoloAnalizza,)