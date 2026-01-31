import os

def TestSemplice():
    with open("/tmp/test_ok.txt", "w") as f:
        f.write("Il ponte Python di LibreOffice FUNZIONA!")

g_exportedScripts = (TestSemplice,)
