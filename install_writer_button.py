import os

def install():
    path = os.path.expanduser("~/.config/libreoffice/4/user/config/soffice.cfg/modules/swriter/toolbar/standardbar.xml")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<toolbar:toolbar xmlns:toolbar="http://openoffice.org/2001/toolbar" xmlns:xlink="http://www.w3.org/1999/xlink" toolbar:label="Standard">
 <toolbar:toolbaritem xlink:href=".uno:NewDoc"/>
 <toolbar:toolbaritem xlink:href=".uno:Open"/>
 <toolbar:toolbaritem xlink:href=".uno:Save"/>
 <toolbar:toolbaritem xlink:href="vnd.sun.star.script:romolo_writer.py$RomoloAnalizza?language=Python&amp;location=user" toolbar:text="Romolo AI" toolbar:label="Romolo AI"/>
 <toolbar:toolbaritem xlink:href=".uno:Cut"/>
 <toolbar:toolbaritem xlink:href=".uno:Copy"/>
 <toolbar:toolbaritem xlink:href=".uno:Paste"/>
</toolbar:toolbar>"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(xml_content)
    print("✅ Pulsante Romolo AI installato correttamente nella barra strumenti!")

if __name__ == "__main__":
    install()
