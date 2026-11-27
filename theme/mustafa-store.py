#!/usr/bin/env python3
import shutil, subprocess
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gtk

CSS = b"""
window { background-color: #07112b; color: #f8fafc; }
.header-lbl { font-size: 20px; font-weight: bold; color: #ffffff; }
.sub-lbl { font-size: 12px; color: #93c5fd; }
.store-card { background-color: rgba(14, 30, 72, 0.92); border: 1.5px solid rgba(56, 189, 248, 0.55); border-radius: 14px; padding: 12px; }
.install-btn { background-color: #0284c7; color: #ffffff; font-weight: bold; border-radius: 10px; padding: 6px 14px; }
"""

APPS = [
    ("Kamera (Cheese)", "Webcam-App für Fotos und Videos", "cheese", "cheese", "camera-photo"),
    ("VLC Media Player", "Spielt alle Videos, Musik und DVDs/CDs ab", "vlc", "vlc", "multimedia-video-player"),
    ("LibreOffice Suite", "Textverarbeitung, Tabellen und Präsentationen", "libreoffice", "libreoffice", "libreoffice-startcenter"),
    ("GIMP Bildbearbeitung", "Bilder malen, schneiden und bearbeiten", "gimp", "gimp", "applications-graphics"),
    ("Luanti (Minecraft-Klon)", "Leichtes 3D-Klötzchen-Spiel", "minetest", "minetest", "applications-games"),
    ("System-Updates installieren", "Aktualisiert alle Pakete über WLAN", "__UPDATE__", "__NONE__", "system-software-update"),
]

class MustafaStore(Gtk.Window):
    def __init__(self):
        super().__init__(title="App Store")
        self.set_default_size(560, 480)
        prov = Gtk.CssProvider(); prov.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), prov, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        for m in ("top", "bottom", "start", "end"): getattr(outer, f"set_margin_{m}")(16)
        self.add(outer)
        hdr = Gtk.Label(label="🛍  App Store", xalign=0); hdr.get_style_context().add_class("header-lbl")
        sub = Gtk.Label(label="Klicke auf Installieren (WLAN erforderlich).", xalign=0); sub.get_style_context().add_class("sub-lbl")
        outer.pack_start(hdr, False, False, 0); outer.pack_start(sub, False, False, 0)
        scroll = Gtk.ScrolledWindow(); scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC); outer.pack_start(scroll, True, True, 0)
        lst = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10); scroll.add(lst)
        for title, desc, pkg, cmd_check, icon in APPS:
            card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12); card.get_style_context().add_class("store-card")
            img = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.DIALOG); img.set_pixel_size(36); card.pack_start(img, False, False, 0)
            txt = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            t = Gtk.Label(xalign=0); t.set_markup(f"<b>{title}</b>")
            d = Gtk.Label(label=desc, xalign=0); d.get_style_context().add_class("sub-lbl")
            txt.pack_start(t, False, False, 0); txt.pack_start(d, False, False, 0); card.pack_start(txt, True, True, 0)
            installed = (cmd_check != "__NONE__" and shutil.which(cmd_check) is not None)
            btn = Gtk.Button(label="✔ Installiert" if installed else ("▶ Starten" if pkg == "__UPDATE__" else "⬇ Installieren"))
            btn.get_style_context().add_class("install-btn")
            if installed: btn.set_sensitive(False)
            btn.connect("clicked", lambda _b, p=pkg, tt=title: subprocess.Popen(["xfce4-terminal", "--title", tt, "-e", f"bash -c \"{'sudo apt update && sudo apt upgrade -y' if p == '__UPDATE__' else 'sudo apt update && sudo apt install -y ' + p}; echo 'Fertig! Enter...'; read\""]))
            card.pack_start(btn, False, False, 0); lst.pack_start(card, False, False, 0)
        self.connect("destroy", Gtk.main_quit); self.show_all()

if __name__ == "__main__":
    MustafaStore(); Gtk.main()
