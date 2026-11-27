#!/usr/bin/env python3
import shutil, subprocess
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gtk

for app in ("cheese", "guvcview"):
    if shutil.which(app):
        subprocess.Popen([app]); raise SystemExit(0)

CSS = b"window { background-color: #07112b; color: #f8fafc; } .card { background-color: rgba(14, 30, 72, 0.92); border: 1.5px solid rgba(56, 189, 248, 0.6); border-radius: 16px; padding: 18px; } .btn { background-color: #0284c7; color: #ffffff; font-weight: bold; border-radius: 10px; padding: 8px 16px; }"

class MustafaKamera(Gtk.Window):
    def __init__(self):
        super().__init__(title="Kamera"); self.set_default_size(420, 230)
        prov = Gtk.CssProvider(); prov.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), prov, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12); box.get_style_context().add_class("card")
        for m in ("top", "bottom", "start", "end"): getattr(box, f"set_margin_{m}")(14)
        self.add(box)
        t = Gtk.Label(); t.set_markup("<b>📷  Kamera</b>")
        info = Gtk.Label(label="Installiere Cheese mit 1 Klick über WLAN oder nimm ein Bildschirmfoto auf:", xalign=0); info.set_line_wrap(True)
        box.pack_start(t, False, False, 0); box.pack_start(info, True, True, 0)
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        b1 = Gtk.Button(label="⬇ Cheese laden"); b1.get_style_context().add_class("btn")
        b1.connect("clicked", lambda *_: subprocess.Popen(["xfce4-terminal", "-e", "bash -c 'sudo apt update && sudo apt install -y cheese && cheese'"]))
        b2 = Gtk.Button(label="🖼 Bildschirmfoto"); b2.get_style_context().add_class("btn")
        b2.connect("clicked", lambda *_: subprocess.Popen(["xfce4-screenshooter"]))
        row.pack_start(b1, True, True, 0); row.pack_start(b2, True, True, 0); box.pack_start(row, False, False, 0)
        self.connect("destroy", Gtk.main_quit); self.show_all()

if __name__ == "__main__":
    MustafaKamera(); Gtk.main()
