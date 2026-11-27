#!/usr/bin/env python3
import subprocess, threading
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

class MustafaBluetooth(Gtk.Window):
    def __init__(self):
        super().__init__(title="Bluetooth Manager"); self.set_default_size(420, 360)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        for m in ("top", "bottom", "start", "end"): getattr(box, f"set_margin_{m}")(12)
        self.add(box)
        top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.lbl_status = Gtk.Label(label="Bluetooth wird geprüft...", xalign=0); top.pack_start(self.lbl_status, True, True, 0)
        for txt, fn in [("Ein", lambda *_: self.run_bt(["power", "on"])), ("Aus", lambda *_: self.run_bt(["power", "off"])), ("Suchen (5s)", lambda *_: self.scan_devices())]:
            b = Gtk.Button(label=txt); b.connect("clicked", fn); top.pack_start(b, False, False, 0)
        box.pack_start(top, False, False, 0)
        scroll = Gtk.ScrolledWindow(); self.listbox = Gtk.ListBox(); scroll.add(self.listbox); box.pack_start(scroll, True, True, 0)
        btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        for txt, act in [("Koppeln", "pair"), ("Verbinden", "connect"), ("Trennen", "disconnect")]:
            b = Gtk.Button(label=txt); b.connect("clicked", lambda *_, a=act: self.action(a)); btns.pack_start(b, True, True, 0)
        box.pack_start(btns, False, False, 0)
        self.connect("destroy", Gtk.main_quit); self.show_all(); self.refresh_list()

    def run_bt(self, args):
        threading.Thread(target=lambda: (subprocess.run(["bluetoothctl"] + args, capture_output=True), GLib.idle_add(self.refresh_list)), daemon=True).start()

    def scan_devices(self):
        self.lbl_status.set_text("Suche nach Geräten...")
        threading.Thread(target=lambda: (subprocess.run(["bluetoothctl", "--timeout", "5", "scan", "on"], capture_output=True), GLib.idle_add(self.refresh_list)), daemon=True).start()

    def refresh_list(self):
        for c in self.listbox.get_children(): self.listbox.remove(c)
        try:
            st = subprocess.run(["bluetoothctl", "show"], capture_output=True, text=True, timeout=3)
            self.lbl_status.set_text("Bluetooth: EIN" if "Powered: yes" in st.stdout else "Bluetooth: AUS")
            res = subprocess.run(["bluetoothctl", "devices"], capture_output=True, text=True, timeout=3)
            for line in res.stdout.splitlines():
                parts = line.split(" ", 2)
                if len(parts) >= 3 and parts[0] == "Device":
                    row = Gtk.ListBoxRow(); row.mac = parts[1]; row.add(Gtk.Label(label=f"{parts[2]} ({parts[1]})", xalign=0)); self.listbox.add(row)
        except Exception as e:
            self.lbl_status.set_text(f"Hinweis: {e}")
        self.listbox.show_all()

    def action(self, cmd):
        row = self.listbox.get_selected_row()
        if not row: return
        def worker():
            if cmd == "pair": subprocess.run(["bluetoothctl", "trust", row.mac], capture_output=True)
            subprocess.run(["bluetoothctl", cmd, row.mac], capture_output=True); GLib.idle_add(self.refresh_list)
        threading.Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    MustafaBluetooth(); Gtk.main()
