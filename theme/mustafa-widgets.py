#!/usr/bin/env python3
import datetime, glob, json, os, subprocess, threading, urllib.request
import cairo, gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib, Gtk

WOCHENTAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
MONATE = ["", "Januar", "Februar", "März", "April", "Mai", "Juni",
          "Juli", "August", "September", "Oktober", "November", "Dezember"]

CSS = b"""
window { background-color: transparent; }
.card {
    background-color: rgba(11, 24, 58, 0.86);
    border: 1.5px solid rgba(56, 189, 248, 0.65);
    border-radius: 16px;
    padding: 12px 14px;
    color: #f1f5f9;
}
.clock-time { font-size: 30px; font-weight: bold; color: #ffffff; }
.clock-date { font-size: 11px; color: #cbd5e1; }
.weather-temp { font-size: 20px; font-weight: bold; color: #fde047; }
.weather-desc { font-size: 11px; color: #bae6fd; }
.card-title { font-size: 13px; font-weight: bold; color: #f8fafc; }
.sub-text { font-size: 11px; color: #93c5fd; }
.stat-label { font-size: 11px; color: #e2e8f0; }
.pill-eco { background-color: rgba(22, 163, 74, 0.25); border: 1px solid rgba(74, 222, 128, 0.6); border-radius: 10px; padding: 4px 10px; color: #86efac; font-size: 11px; font-weight: bold; }
.pill-turbo { background-color: rgba(234, 179, 8, 0.22); border: 1px solid rgba(250, 204, 21, 0.75); border-radius: 10px; padding: 4px 10px; color: #fde047; font-size: 11px; font-weight: bold; }
.check-line { font-size: 11px; color: #cbd5e1; }
progressbar trough { min-height: 7px; border-radius: 5px; background-color: rgba(15, 23, 42, 0.85); }
progressbar progress { min-height: 7px; border-radius: 5px; background-image: linear-gradient(to right, #22c55e, #38bdf8); }
"""

def read_mem():
    info = {}
    with open("/proc/meminfo", "r") as f:
        for line in f:
            k, v = line.split(":", 1)
            info[k] = int(v.strip().split()[0])
    total_mb = info.get("MemTotal", 1) // 1024
    avail_mb = info.get("MemAvailable", info.get("MemFree", 0)) // 1024
    used_mb = max(0, total_mb - avail_mb)
    pct = int(round((used_mb / max(1, total_mb)) * 100))
    return used_mb, total_mb, pct

def read_cpu_raw():
    with open("/proc/stat", "r") as f:
        parts = [int(x) for x in f.readline().split()[1:8]]
    return parts[3] + parts[4], sum(parts)

def read_battery():
    for bat in sorted(glob.glob("/sys/class/power_supply/BAT*")):
        try:
            cap = int(open(os.path.join(bat, "capacity")).read().strip())
            st = open(os.path.join(bat, "status")).read().strip()
            return cap, st
        except Exception:
            pass
    return None, "Netzbetrieb"

class MustafaWidgets(Gtk.Window):
    def __init__(self):
        super().__init__(title="System Widgets")
        self.prev_idle, self.prev_total = read_cpu_raw()
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.set_default_size(310, -1)
        self.set_resizable(False)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
            self.set_app_paintable(True)
            self.connect("draw", self.on_draw)
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_type_hint(Gdk.WindowTypeHint.DESKTOP)
        self.stick()

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        for m in ("top", "bottom", "start", "end"):
            getattr(outer, f"set_margin_{m}")(10)
        self.add(outer)

        card1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        card1.get_style_context().add_class("card")
        outer.add(card1)
        c1_left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.lbl_time = Gtk.Label(xalign=0); self.lbl_time.get_style_context().add_class("clock-time")
        self.lbl_date = Gtk.Label(xalign=0); self.lbl_date.get_style_context().add_class("clock-date")
        c1_left.pack_start(self.lbl_time, False, False, 0); c1_left.pack_start(self.lbl_date, False, False, 0)
        card1.pack_start(c1_left, True, True, 0)
        c1_right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.lbl_temp = Gtk.Label(label="☀ --°C", xalign=1); self.lbl_temp.get_style_context().add_class("weather-temp")
        self.lbl_city = Gtk.Label(label="Lädt Wetter...", xalign=1); self.lbl_city.get_style_context().add_class("weather-desc")
        c1_right.pack_start(self.lbl_temp, False, False, 0); c1_right.pack_start(self.lbl_city, False, False, 0)
        card1.pack_start(c1_right, False, False, 0)

        card2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=7)
        card2.get_style_context().add_class("card")
        outer.add(card2)
        t2 = Gtk.Label(label="⚙  System Status", xalign=0); t2.get_style_context().add_class("card-title")
        card2.pack_start(t2, False, False, 0)
        self.lbl_ram, self.bar_ram = self.make_stat_row(card2, "RAM")
        self.lbl_cpu, self.bar_cpu = self.make_stat_row(card2, "CPU")
        self.lbl_bat, self.bar_bat = self.make_stat_row(card2, "Akku")
        self.lbl_mode = Gtk.Label(label="🌿 Sehr sparsam"); self.lbl_mode.get_style_context().add_class("pill-eco")
        card2.pack_start(self.lbl_mode, False, False, 2)

        card3 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        card3.get_style_context().add_class("card")
        outer.add(card3)
        top3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        top3_lbls = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
        t3 = Gtk.Label(label="👑  Smart Turbo", xalign=0); t3.get_style_context().add_class("card-title")
        s3 = Gtk.Label(label="Automatisch. Intelligent. Stark.", xalign=0); s3.get_style_context().add_class("sub-text")
        top3_lbls.pack_start(t3, False, False, 0); top3_lbls.pack_start(s3, False, False, 0)
        top3.pack_start(top3_lbls, True, True, 0)
        self.turbo_switch = Gtk.Switch(); self.turbo_switch.set_valign(Gtk.Align.CENTER)
        self.turbo_switch.connect("notify::active", self.on_turbo_toggle)
        top3.pack_start(self.turbo_switch, False, False, 0)
        card3.pack_start(top3, False, False, 0)
        for txt in ["✓  Erkennt, was du machst", "✓  Spart Akku beim Surfen", "✓  Volle Leistung bei Spielen", "✓  Räumt RAM automatisch auf"]:
            l = Gtk.Label(label=txt, xalign=0); l.get_style_context().add_class("check-line"); card3.pack_start(l, False, False, 0)
        self.lbl_turbo_info = Gtk.Label(label="", xalign=0); self.lbl_turbo_info.get_style_context().add_class("sub-text")
        card3.pack_start(self.lbl_turbo_info, False, False, 0)

        self.connect("destroy", Gtk.main_quit)
        self.update_stats()
        GLib.timeout_add_seconds(2, self.update_stats)
        threading.Thread(target=self.fetch_weather, daemon=True).start()
        GLib.timeout_add_seconds(1800, self.trigger_weather)
        self.show_all()
        self.position_top_right()

    def make_stat_row(self, parent, name):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        n_lbl = Gtk.Label(label=name, xalign=0); n_lbl.get_style_context().add_class("stat-label")
        val_lbl = Gtk.Label(label="--", xalign=1); val_lbl.get_style_context().add_class("stat-label")
        row.pack_start(n_lbl, True, True, 0); row.pack_start(val_lbl, False, False, 0)
        bar = Gtk.ProgressBar(); bar.set_hexpand(True)
        box.pack_start(row, False, False, 0); box.pack_start(bar, False, False, 0)
        parent.pack_start(box, False, False, 0)
        return val_lbl, bar

    def on_draw(self, widget, cr):
        cr.set_source_rgba(0, 0, 0, 0); cr.set_operator(cairo.OPERATOR_SOURCE); cr.paint(); return False

    def position_top_right(self):
        disp = Gdk.Display.get_default()
        mon = disp.get_primary_monitor() or disp.get_monitor(0)
        if mon:
            geo = mon.get_geometry(); w, _ = self.get_size()
            self.move(geo.x + geo.width - w - 22, geo.y + 40)

    def update_stats(self):
        now = datetime.datetime.now()
        self.lbl_time.set_text(now.strftime("%H:%M"))
        self.lbl_date.set_text(f"{WOCHENTAGE[now.weekday()]}, {now.day}. {MONATE[now.month]} {now.year}")
        used_mb, total_mb, ram_pct = read_mem()
        self.lbl_ram.set_text(f"{used_mb} MB ({ram_pct}%)"); self.bar_ram.set_fraction(min(1.0, ram_pct / 100.0))
        idle, total = read_cpu_raw()
        di, dt = idle - self.prev_idle, max(1, total - self.prev_total)
        cpu_pct = max(0, min(100, int(round(100.0 * (dt - di) / dt))))
        self.prev_idle, self.prev_total = idle, total
        self.lbl_cpu.set_text(f"{cpu_pct}%"); self.bar_cpu.set_fraction(cpu_pct / 100.0)
        cap, status = read_battery()
        if cap is None:
            self.lbl_bat.set_text("Netzbetrieb"); self.bar_bat.set_fraction(1.0)
        else:
            self.lbl_bat.set_text(("⚡" if status == "Charging" else "") + f"{cap}%"); self.bar_bat.set_fraction(min(1.0, cap / 100.0))
        return True

    def trigger_weather(self):
        threading.Thread(target=self.fetch_weather, daemon=True).start(); return True

    def fetch_weather(self):
        try:
            req = urllib.request.Request("https://wttr.in/?format=j1&lang=de", headers={"User-Agent": "curl/8.0"})
            with urllib.request.urlopen(req, timeout=5) as resp: data = json.loads(resp.read().decode("utf-8"))
            cur = data["current_condition"][0]
            temp = cur.get("temp_C", "--")
            area = data.get("nearest_area", [{}])[0].get("areaName", [{}])[0].get("value", "Lokal")
            desc = cur["lang_de"][0].get("value", "") if cur.get("lang_de") else ""
            GLib.idle_add(self.set_weather_ui, f"☀ {temp}°C", f"{desc} • {area}" if desc else area)
        except Exception:
            GLib.idle_add(self.set_weather_ui, "☀ --°C", "Offline (kein WLAN)")

    def set_weather_ui(self, t, d):
        self.lbl_temp.set_text(t); self.lbl_city.set_text(d)

    def on_turbo_toggle(self, switch, _pspec):
        active = switch.get_active()
        ctx = self.lbl_mode.get_style_context()
        if active:
            ctx.remove_class("pill-eco"); ctx.add_class("pill-turbo")
            self.lbl_mode.set_text("⚡ Smart Turbo aktiv"); msg = "Leistung hoch & RAM aufgeräumt"
        else:
            ctx.remove_class("pill-turbo"); ctx.add_class("pill-eco")
            self.lbl_mode.set_text("🌿 Sehr sparsam"); msg = "Energiesparmodus aktiv"
        if os.path.exists("/usr/local/bin/mustafa-turbo"):
            subprocess.Popen(["sudo", "-n", "/usr/local/bin/mustafa-turbo", "on" if active else "off"])
        self.lbl_turbo_info.set_text(msg)

if __name__ == "__main__":
    MustafaWidgets(); Gtk.main()
