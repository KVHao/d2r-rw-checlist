# -*- coding: utf-8 -*-
"""KVHao v11 — reduce CPU overhead without slowing critical HP/MP reading.

Applied after v10 game-process patch and before build-time display localization.
No changes to game-memory offsets, potion decisions, or key bindings.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
app = root / "ui" / "app.py"
reader = root / "d2r" / "reader.py"
watcher = root / "d2r" / "watcher.py"
for p in (app,reader,watcher):
    if not p.is_file():
        raise RuntimeError("Missing upstream source: " + str(p))

def once(src, before, after, label):
    n = src.count(before)
    if n != 1:
        raise RuntimeError(f"{label}: upstream changed (expected 1 anchor, got {n})")
    return src.replace(before, after, 1)

a = app.read_text(encoding="utf-8")
# The v10 background structural scan may run for up to 90s while the UI
# starts a new worker every 5s. Only allow one worker (even if started from
# automatic connect and subsequent periodic retries).
a = once(a,
    "        self._last_discover = 0.0",
    """        self._last_discover = 0.0
        self._discover_lock = threading.Lock()""",
    "scan lock initialization")
a = once(a,
    """    def _background_discover(self):
        \"\"\"Try the structural UnitTable scan in the background after connect.\"\"\"
        if not self.reader:
            return
        off = self.reader.discover()
        if off:
            self._set_status("Connected", GOOD)
            self.on_event(m.GameEvent(kind="info",
                          message=f"Resolved UnitTable offset structurally at 0x{off:X}."))
        else:
            self._set_status("Offsets unresolved", WARN)
            self.on_event(m.GameEvent(kind="error",
                          message="Could not auto-find offsets. Open Diagnostics → Run scan while in a game."))
""",
    """    def _background_discover(self):
        \"\"\"Single bounded automatic scan; prevent overlapping workers.\"\"\"
        reader = self.reader
        if reader is None or reader.offsets.ok:
            return
        if not self._discover_lock.acquire(blocking=False):
            return
        try:
            # An older worker must not change UI status after a reconnect.
            if reader is not self.reader or reader.offsets.ok:
                return
            off = reader.discover(fast=True)
            if reader is not self.reader:
                return
            if off:
                self._set_status("Connected", GOOD)
                self.on_event(m.GameEvent(kind="info",
                              message=f"Resolved UnitTable offset structurally at 0x{off:X}."))
            else:
                self._set_status("Offsets unresolved", WARN)
                self.on_event(m.GameEvent(kind="info",
                              message="Quick scan incomplete; use Diagnostics to scan all modules."))
        except Exception as exc:
            if reader is self.reader:
                self.on_event(m.GameEvent(kind="error",
                              message=f"Auto-scan failed: {exc}"))
        finally:
            self._discover_lock.release()
""",
    "exclusive structural scan")
a = once(a,
    "                        if now - self._last_discover > 5:",
    "                        if now - self._last_discover > 90:",
    "scan retry throttle")
a = once(a,
    "        self.after(150, self._poll)",
    "        self.after(250, self._poll)",
    "initial GUI refresh")
a = once(a,
    "        self.after(150, self._poll)",
    "        self.after(250, self._poll)",
    "repeating GUI refresh")
app.write_text(a,encoding="utf-8")

r = reader.read_text(encoding="utf-8")
r = once(r,
    """        return self._count_monsters(radius, engaged_only=True)

    def _count_monsters""",
    """        # Monster enumeration is much more expensive than HP/MP reads.
        # Cache up to 400ms; preserve the independent 50ms vitals loop.
        now = time.monotonic()
        last = getattr(self, "_engaged_sample_at", -100.0)
        if (now - last < 0.40
                and getattr(self, "_engaged_sample_radius", None) == radius):
            return getattr(self, "_engaged_sample_count", -1)
        result = self._count_monsters(radius, engaged_only=True)
        self._engaged_sample_count = result
        self._engaged_sample_radius = radius
        self._engaged_sample_at = now
        return result

    def _count_monsters""",
    "monster enumeration cache")
r = once(r,
    "    def discover(self) -> int:",
    "    def discover(self, fast: bool = False) -> int:",
    "two scan modes")
r = once(r,
    """        base, off = discover_unit_table(self.proc, modules=modules, stats=stats)
""",
    """        if fast:
            # Scan plausible game-bearing images only. An explicit Diagnostics
            # scan still uses the original exhaustive scan for other builds.
            preferred = [m for m in modules if m[2].casefold().endswith(
                ("d2r.exe", "d2rloader.exe", "d2rcore.dll"))]
            modules = preferred or [(
                self.proc.module_base, self.proc.module_size, self.proc.module_name)]
        base, off = discover_unit_table(
            self.proc, modules=modules, stats=stats,
            time_budget=8.0 if fast else 90.0)
""",
    "bounded fast scan vs exhaustive diagnostics")
reader.write_text(r,encoding="utf-8")

w = watcher.read_text(encoding="utf-8")
w = once(w,
    "    FULL_INTERVAL_SEC = 0.25",
    "    FULL_INTERVAL_SEC = 0.65",
    "expensive complete snapshot throttle")
watcher.write_text(w,encoding="utf-8")

print("KVHao v11 optimization OK: critical HP/MP remain 50 ms; "
      "monster scan cached 400 ms; full snapshots 650 ms; "
      "GUI redraw 250 ms; auto-scans serialized and bounded.")
