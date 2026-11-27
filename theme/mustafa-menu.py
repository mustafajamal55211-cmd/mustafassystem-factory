#!/usr/bin/env python3
import glob, os, shutil, subprocess
import cairo, gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import Gdk, GdkPixbuf, Gtk

CSS = b"""
window { background-color: transparent; }
.menu-frame { background-color: rgba(10, 22, 54, 0.94); border: 1.5px solid rgba(56, 189, 248, 0.75); border-radius: 18px; padding: 14px; color: #f8fafc; }
.search-entry { background-color: rgba(15, 34, 80, 0.9); border: 1px solid rgba(96, 165, 250, 0.6); border-radius: 12px; padding: 8px 12px; color: #ffffff; font-size: 13px; }
.side-btn { background: transparent; border: none; border-radius: 10px; padding: 6px 10px; color: #cbd5e1; font-size: 12px; }
.side-btn:hover { background-color: rgba(56, 189, 248, 0.18); color: #ffffff; }
.side-btn-active { background-color: rgba(56, 189, 248, 0.28); border: 1px solid rgba(56, 189, 248, 0.6); color: #ffffff; font-weight: bold; }
.section-title { font-size: 13px; font-weight: bold; color: #fde047; margin-bottom: 4px; }
.app-tile { background-color: rgba(20, 42, 92, 0.75); border: 1px solid rgba(96, 165, 250, 0.35); border-radius: 14px; padding: 7px 6px; color: #f1f5f9; font-size: 11px; }
.app-tile:hover { background-color: rgba(56, 189, 248, 0.28); border-color: rgba(125, 211, 252, 0.9); }
.quote-txt { font-size: 10px; font-style: italic; color: #93c5fd; }
.power-btn { background-color: rgba(239, 68, 68, 0.22); border: 1px solid rgba(248, 113, 113, 0.55); border-radius: 10px; padding: 8px 12px; color: #fecaca; font-weight: bold; }
"""

def open_cmd(cmd):
    subprocess.Popen(cmd, shell=True, start_new_session=True)

def pick_browser_url(url):
    for b in ("firefox-esr", "firefox", "chromium", "xdg-open"):
        if shutil.which(b): return f"{b} '{url}'"
    return f"xdg-open '{url}'"

FAVORITEN = [
    ("Browser", "firefox-esr", lambda: pick_browser_url("https://www.google.de")),
    ("Google Play / Android", "phone", lambda: "python3 /usr/local/bin/mustafa-waydroid.py"),
    ("KI Assistent", "applications-science", lambda: pick_browser_url("https://gemini.google.com")),
    ("Kamera", "camera-photo", lambda: "python3 /usr/local/bin/mustafa-kamera.py"),
    ("Explorer", "system-file-manager", lambda: "thunar || dolphin || nautilus || pcmanfm"),
    ("Terminal", "utilities-terminal", lambda: "xfce4-terminal || konsole || gnome-terminal"),
    ("Einstellungen", "preferences-system", lambda: "xfce4-settings-manager || systemsettings || gnome-control-center"),
    ("App Store", "system-software-install", lambda: "python3 /usr/local/bin/mustafa-store.py"),
    ("Spotify", "multimedia-audio-player", lambda: pick_browser_url("https://open.spotify.com")),
    ("Discord", "internet-chat", lambda: pick_browser_url("https://discord.com/app")),
    ("Instagram", "emblem-photos", lambda: pick_browser_url("https://www.instagram.com")),
    ("Bluetooth", "bluetooth", lambda: "python3 /usr/local/bin/mustafa-bluetooth.py"),
]

WEBAPPS = [
    ("Gemini AI", "applications-science", lambda: pick_browser_url("https://gemini.google.com")),
    ("Spotify", "multimedia-audio-player", lambda: pick_browser_url("https://open.spotify.com")),
    ("Discord", "internet-chat", lambda: pick_browser_url("https://discord.com/app")),
    ("Instagram", "emblem-photos", lambda: pick_browser_url("https://www.instagram.com")),
    ("YouTube", "multimedia-video-player", lambda: pick_browser_url("https://www.youtube.com")),
    ("Suche", "web-browser", lambda: pick_browser_url("https://www.google.de")),
]

KI_APPS = [
    ("Gemini AI", "applications-science", lambda: pick_browser_url("https://gemini.google.com")),
    ("ChatGPT", "applications-internet", lambda: pick_browser_url("https://chatgpt.com")),
    ("Wikipedia", "accessories-dictionary", lambda: pick_browser_url("https://de.wikipedia.org")),
]

EINSTELLUNGEN = [
    ("Alle Einstellungen", "preferences-system", lambda: "xfce4-settings-manager"),
    ("WLAN verwalten", "network-wireless", lambda: "nm-connection-editor"),
    ("Bluetooth Manager", "bluetooth", lambda: "python3 /usr/local/bin/mustafa-bluetooth.py"),
    ("Android / Google Play", "phone", lambda: "python3 /usr/local/bin/mustafa-waydroid.py"),
    ("Bildschirm", "preferences-desktop-display", lambda: "xfce4-display-settings"),
    ("Energieverwaltung", "battery", lambda: "xfce4-power-manager-settings"),
]

DATEIEN = [
    ("Persönlicher Ordner", "user-home", lambda: "thunar ~"),
    ("Dieser PC", "computer", lambda: "thunar computer:///"),
    ("Papierkorb", "user-trash", lambda: "thunar trash:///"),
    ("CD / SD-Karten", "drive-optical", lambda: "thunar"),
]

SICHERHEIT = [
    ("Passwort ändern", "dialog-password", lambda: "xfce4-terminal -e 'passwd'"),
    ("App Store (Updates)", "system-software-update", lambda: "python3 /usr/local/bin/mustafa-store.py"),
]

PFLEGE = [
    ("RAM aufräumen", "edit-clear", lambda: "sudo -n /usr/local/bin/mustafa-turbo on"),
    ("Task-Manager", "utilities-system-monitor", lambda: "xfce4-taskmanager"),
    ("Widgets neu starten", "view-refresh", lambda: "pkill -f mustafa-widgets.py; python3 /usr/local/bin/mustafa-widgets.py"),
    ("Bildschirmfoto", "applets-screenshooter", lambda: "xfce4-screenshooter"),
    ("App Store", "system-software-install", lambda: "python3 /usr/local/bin/mustafa-store.py"),
]

def load_system_apps():
    apps, seen = [], set()
    for d in ("/usr/share/applications", os.path.expanduser("~/.local/share/applications")):
        if not os.path.isdir(d): continue
        for p in sorted(glob.glob(os.path.join(d, "*.desktop"))):
            name, icon, exec_cmd, nodisp = "", "application-x-executable", "", False
            try:
                with open(p, encoding="utf-8", errors="ignore") as f:
                    in_entry = False
                    for line in f:
                        line = line.strip()
                        if line == "[Desktop Entry]": in_entry = True; continue
                        if line.startswith("[") and line != "[Desktop Entry]": in_entry = False
                        if not in_entry or "=" not in line: continue
                        k, v = line.split("=", 1)
                        if k == "Name" and not name: name = v
                        elif k == "Name[de]": name = v
                        elif k == "Icon": icon = v
                        elif k == "Exec": exec_cmd = v.split("%")[0].strip()
                        elif k == "NoDisplay" and v.lower() == "true": nodisp = True
                if name and exec_cmd and not nodisp and name not in seen:
                    seen.add(name); apps.append((name, icon, lambda c=exec_cmd: c))
            except Exception: pass
    return apps

class MustafaMenu(Gtk.Window):
    def __init__(self):
        super().__init__(title="System Menü")
        self.all_apps = load_system_apps()
        self.current_cat = "favoriten"
        provider = Gtk.CssProvider(); provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.set_default_size(690, 520); self.set_resizable(False)
        screen = self.get_screen(); visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual); self.set_app_paintable(True); self.connect("draw", self.on_draw)
        self.set_decorated(False); self.set_skip_taskbar_hint(True)
        self.connect("focus-out-event", lambda *_: Gtk.main_quit())
        self.connect("key-press-event", lambda _w, e: Gtk.main_quit() if e.keyval == Gdk.KEY_Escape else None)
        self.connect("destroy", Gtk.main_quit)

        frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10); frame.get_style_context().add_class("menu-frame")
        for m in ("top", "bottom", "start", "end"): getattr(frame, f"set_margin_{m}")(6)
        self.add(frame)

        top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        if os.path.exists("/usr/share/mustafa/logo-round-64.png"):
            pb = GdkPixbuf.Pixbuf.new_from_file_at_size("/usr/share/mustafa/logo-round-64.png", 36, 36)
            top.pack_start(Gtk.Image.new_from_pixbuf(pb), False, False, 0)
        self.search = Gtk.Entry(); self.search.set_placeholder_text("🔍  Apps, Dateien, Einstellungen suchen...")
        self.search.get_style_context().add_class("search-entry"); self.search.connect("changed", lambda *_: self.refresh_grid())
        top.pack_start(self.search, True, True, 0); frame.pack_start(top, False, False, 0)

        body = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12); frame.pack_start(body, True, True, 0)
        left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3); left.set_size_request(180, -1); body.pack_start(left, False, False, 0)

        self.cat_btns = {}
        for key, label in [
            ("favoriten", "⭐  Favoriten"), ("apps", "⊞  Apps"), ("webapps", "🌐  Web-Apps"),
            ("einstellungen", "⚙  Einstellungen"), ("dateien", "📁  Dateien"), ("ki", "🧠  KI & Assistent"),
            ("sicherheit", "🛡  Sicherheit"), ("pflege", "✨  Systempflege"), ("energie", "🌿  Energie"),
        ]:
            b = Gtk.Button(label=label)
            if b.get_child(): b.get_child().set_xalign(0.0)
            b.get_style_context().add_class("side-btn"); b.connect("clicked", self.on_cat, key)
            left.pack_start(b, False, False, 0); self.cat_btns[key] = b

        spacer = Gtk.Box(); spacer.set_vexpand(True); left.pack_start(spacer, True, True, 0)
        quote = Gtk.Label(label="„Ein besseres Morgen\nbeginnt mit einem\nstarken System.“\n♡ Mustafa", xalign=0)
        quote.get_style_context().add_class("quote-txt"); left.pack_start(quote, False, False, 4)

        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6); body.pack_start(right_box, True, True, 0)
        self.cat_title = Gtk.Label(label="👑  Apps", xalign=0); self.cat_title.get_style_context().add_class("section-title")
        right_box.pack_start(self.cat_title, False, False, 0)
        scroll = Gtk.ScrolledWindow(); scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        right_box.pack_start(scroll, True, True, 0)
        self.flow = Gtk.FlowBox(); self.flow.set_valign(Gtk.Align.START)
        self.flow.set_max_children_per_line(3); self.flow.set_min_children_per_line(3)
        self.flow.set_column_spacing(8); self.flow.set_row_spacing(8); self.flow.set_selection_mode(Gtk.SelectionMode.NONE)
        scroll.add(self.flow)

        self.select_cat("favoriten"); self.show_all()
        disp = Gdk.Display.get_default(); mon = disp.get_primary_monitor() or disp.get_monitor(0)
        if mon:
            geo = mon.get_geometry(); _, h = self.get_size()
            self.move(geo.x + 18, geo.y + geo.height - h - 66)
        self.search.grab_focus()

    def on_draw(self, w, cr):
        cr.set_source_rgba(0, 0, 0, 0); cr.set_operator(cairo.OPERATOR_SOURCE); cr.paint(); return False

    def on_cat(self, _b, key):
        self.search.set_text(""); self.select_cat(key)

    def select_cat(self, key):
        self.current_cat = key
        for k, b in self.cat_btns.items():
            b.get_style_context().add_class("side-btn-active") if k == key else b.get_style_context().remove_class("side-btn-active")
        self.refresh_grid()

    def refresh_grid(self):
        for child in self.flow.get_children(): self.flow.remove(child)
        q = self.search.get_text().strip().lower()
        if q:
            self.cat_title.set_text(f"🔍  Suche: {q}")
            items = [x for x in (FAVORITEN + WEBAPPS + KI_APPS + self.all_apps) if q in x[0].lower()]
            seen, unique = set(), []
            for it in items:
                if it[0] not in seen: seen.add(it[0]); unique.append(it)
            items = unique[:24]
        elif self.current_cat == "energie":
            self.cat_title.set_text("🌿  Energie & Sitzung")
            for label, cmd in [
                ("⏻  Herunterfahren", "systemctl poweroff || xfce4-session-logout --halt"),
                ("↻  Neu starten", "systemctl reboot || xfce4-session-logout --reboot"),
                ("🔒  Abmelden", "xfce4-session-logout --logout"),
                ("🌙  Energiesparen", "systemctl suspend"),
                ("⚡  Turbo EIN", "sudo -n /usr/local/bin/mustafa-turbo on"),
                ("🌿  Sparmodus", "sudo -n /usr/local/bin/mustafa-turbo off"),
            ]:
                b = Gtk.Button(label=label); b.get_style_context().add_class("power-btn"); b.set_size_request(140, 56)
                b.connect("clicked", lambda _w, c=cmd: (open_cmd(c), Gtk.main_quit()))
                self.flow.add(b)
            self.flow.show_all(); return
        else:
            mapping = {
                "favoriten": ("👑  Favoriten & Android", FAVORITEN), "apps": ("⊞  Alle installierten Apps", self.all_apps),
                "webapps": ("🌐  Web-Apps", WEBAPPS), "einstellungen": ("⚙  Einstellungen", EINSTELLUNGEN),
                "dateien": ("📁  Dateien & Laufwerke", DATEIEN), "ki": ("🧠  KI & Assistent", KI_APPS),
                "sicherheit": ("🛡  Sicherheit", SICHERHEIT), "pflege": ("✨  Systempflege", PFLEGE),
            }
            title, items = mapping.get(self.current_cat, ("Apps", FAVORITEN))
            self.cat_title.set_text(title)
        for name, icon_name, cmd_fn in items:
            btn = Gtk.Button(); btn.get_style_context().add_class("app-tile"); btn.set_size_request(138, 82)
            vb = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5); vb.set_halign(Gtk.Align.CENTER); vb.set_valign(Gtk.Align.CENTER)
            img = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DIALOG); img.set_pixel_size(32)
            lbl = Gtk.Label(label=name); lbl.set_max_width_chars(16); lbl.set_ellipsize(3)
            vb.pack_start(img, False, False, 0); vb.pack_start(lbl, False, False, 0); btn.add(vb)
            btn.connect("clicked", lambda _w, fn=cmd_fn: (open_cmd(fn()), Gtk.main_quit()))
            self.flow.add(btn)
        self.flow.show_all()

if __name__ == "__main__":
    MustafaMenu(); Gtk.main()
