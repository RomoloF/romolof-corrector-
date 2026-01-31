import os
import gi
gi.require_version('Gedit', '3.0')
from gi.repository import GObject, Gedit, Gtk

class RomoloGeditPlugin(GObject.Object, Gedit.WindowActivatable):
    window = GObject.Property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self._add_menu_item()

    def _add_menu_item(self):
        action = Gtk.Action(name="RomoloAction", label="Romolo: Analizza e correggi", tooltip="Correggi con AI", stock_id=None)
        action.connect("activate", self.on_romolo_clicked)
        self.action_group = Gtk.ActionGroup(name="RomoloGroup")
        self.action_group.add_action(action)
        manager = self.window.get_ui_manager()
        manager.insert_action_group(self.action_group, -1)
        self.ui_id = manager.add_ui_from_string("""
            <ui>
              <menubar name="MenuBar">
                <menu action="ToolsMenu">
                  <placeholder name="ToolsOps_2">
                    <menuitem action="RomoloAction"/>
                  </placeholder>
                </menu>
              </menubar>
            </ui>
        """)

    def on_romolo_clicked(self, action):
        os.system("python3 /home/romolo/Scrivania/gemini-corrector/romolo_desktop.py &")

    def do_deactivate(self):
        manager = self.window.get_ui_manager()
        manager.remove_ui(self.ui_id)
        manager.remove_action_group(self.action_group)
