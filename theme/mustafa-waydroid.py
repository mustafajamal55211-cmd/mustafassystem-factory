#!/usr/bin/env python3
import os, shutil, sqlite3, subprocess, webbrowser
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gtk

HAS_IMG = os.path.exists("/var/lib/waydroid/images/system.img")

def launch_waydroid_now():
    subprocess.run(["sudo", "-n", "systemctl", "start", "waydroid-container"], capture_output=True)
    if os.environ.get("WAYLAND_DISPLAY"):
        subprocess.Popen(["waydroid", "show-full-ui"])
    elif shutil.which("cage"):
        subprocess.Popen(["cage", "--", "waydroid", "show-full-ui"])
    elif shutil.which("weston"):
        subprocess.Popen(["weston", "--", "waydroid", "show-full-ui"])
    else:
        subprocess.Popen(["waydroid", "show-full-ui"])

CSS = b"""
window { background-color: #07112b; color: #f8fafc; }
.card { background-color: rgba(14, 30, 72, 0.92); border: 1.5px solid rgba(56, 189, 248, 0.65); border-radius: 16px; padding: 18px; }
.btn { background-color: #16a34a; color: #ffffff; font-weight: bold; border-radius: 10px; padding: 10px 14px; }
.btn-blue { background-color: #0284c7; color: #ffffff; font-weight: bold; border-radius: 10px; padding: 10px 14px; }
"""

def find_android_id():
    for root, _dirs, files in os.walk("/var/lib/waydroid/data"):
        if "gservices.db" in files:
            try:
                con = sqlite3.connect(os.path.join(root, "gservices.db"))
                cur = con.execute("SELECT value FROM main WHERE name='android_id' LIMIT 1")
                row = cur.fetchone()
                con.close()
                if row:
                    return str(row[0])
            except Exception:
                pass
    try:
        out = subprocess.check_output(
            ["sudo", "-n", "waydroid", "shell", "--", "sh", "-c",
             "sqlite3 /data/data/com.google.android.gsf/databases/gservices.db \"select value from main where name='android_id';\""],
            text=True, timeout=5
        ).strip()
        if out.isdigit():
            return out
    except Exception:
        pass
    return ""

class MustafaWaydroid(Gtk.Window):
    def __init__(self):
        super().__init__(title="Android & Google Play (Waydroid auf Wayland)")
        self.set_default_size(500, 310)
        prov = Gtk.CssProvider()
        prov.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), prov, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.get_style_context().add_class("card")
        for m in ("top", "bottom", "start", "end"):
            getattr(box, f"set_margin_{m}")(14)
        self.add(box)

        t = Gtk.Label()
        t.set_markup("<b>📱  Android &amp; Google Play (Waydroid über Wayland)</b>")
        msg = (
            "Android mit Google Play (GAPPS) ist eingerichtet!\nStarte Android über Wayland oder hole dir deine Google-Play-Zertifizierungs-ID:"
            if HAS_IMG else
            "Waydroid ist bereit! Beim ersten Start lädt es einmalig Android INKLUSIVE Google Play Store (GAPPS, ca. 900 MB über WLAN) herunter."
        )
        info = Gtk.Label(label=msg, xalign=0)
        info.set_line_wrap(True)
        box.pack_start(t, False, False, 0)
        box.pack_start(info, True, True, 0)

        self.id_entry = Gtk.Entry()
        self.id_entry.set_placeholder_text("Hier erscheint deine Android-ID für Google Play...")
        box.pack_start(self.id_entry, False, False, 0)

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        b_start = Gtk.Button(label="▶ Android + Play Store starten" if HAS_IMG else "⬇ Android + Google Play einrichten")
        b_start.get_style_context().add_class("btn")
        b_start.connect("clicked", self.on_start)
        row.pack_start(b_start, True, True, 0)

        b_cert = Gtk.Button(label="🔑 Google Play ID &amp; Registrieren")
        b_cert.get_style_context().add_class("btn-blue")
        b_cert.connect("clicked", self.on_cert)
        row.pack_start(b_cert, True, True, 0)
        box.pack_start(row, False, False, 0)

        self.connect("destroy", Gtk.main_quit)
        self.show_all()

    def on_start(self, _btn):
        if HAS_IMG and shutil.which("waydroid"):
            launch_waydroid_now()
            Gtk.main_quit()
            return
        cmd = (
            "sudo modprobe binder_linux devices=binder,hwbinder,vndbinder 2>/dev/null || true; "
            "if ! command -v waydroid >/dev/null; then "
            "echo 'deb http://deb.debian.org/debian trixie-backports main contrib non-free-firmware' | sudo tee /etc/apt/sources.list.d/backports.list; "
            "sudo apt update && sudo apt install -y -t trixie-backports waydroid; fi; "
            "sudo waydroid init -s GAPPS -f && sudo systemctl enable --now waydroid-container; "
            "echo 'Fertig! Starte Android mit Google Play...'; "
            "cage -- waydroid show-full-ui"
        )
        subprocess.Popen(["xfce4-terminal", "--title", "Waydroid + Google Play Setup", "-e", f"bash -c \"{cmd}; read\""])

    def on_cert(self, _btn):
        aid = find_android_id()
        if aid:
            self.id_entry.set_text(aid)
        else:
            self.id_entry.set_text("Bitte erst einmal Android starten & kurz warten, dann nochmal klicken!")
        webbrowser.open("https://www.google.com/android/uncertified/")

if __name__ == "__main__":
    MustafaWaydroid()
    Gtk.main()
