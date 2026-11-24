# -*- coding: utf-8 -*-
"""v12 fix: restore broader UnitTable search without the laggy scan loop.

The v11 8-second scan of only a couple of modules can fail to find a
D2RLoader-hosted game's UnitTable even though the game is running.
This patch keeps v11 anti-overlap and 50ms HP/MP polling, makes the numpy
structural prefilter linear, broadens fallback coverage, and fixes active
module size after a successful scan.
"""
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve()
offsets=root/"d2r"/"offsets.py"
reader=root/"d2r"/"reader.py"
app=root/"ui"/"app.py"

def once(src, before, after, label):
    num=src.count(before)
    if num!=1:
        raise RuntimeError(f"{label}: expected 1 anchor, found {num}")
    return src.replace(before, after, 1)

s=offsets.read_text(encoding="utf-8")
s=once(s,
    """        nz = (vals != 0).astype(np.int32)
        counts = np.convolve(nz, np.ones(window, dtype=np.int32), mode="valid")""",
    """        # Rolling count by prefix sum: O(n), not expensive O(n*128)
        # convolution across multi-megabyte game module images.
        nz = (vals != 0).astype(np.uint8)
        prefix = np.empty(n + 1, dtype=np.int32)
        prefix[0] = 0
        np.cumsum(nz, dtype=np.int32, out=prefix[1:])
        counts = prefix[window:] - prefix[:-window]""",
    "linear-time structural prefilter")
s=once(s,
    """            for i in [int(x) for x in np.nonzero(counts >= threshold)[0]]:
                stats[key] += 1
                _classify(i)
                v = _validate_table_window(proc, memory, base, i)
                if v > best_v:
                    best_v = v
                    best_i = i
                if _time.monotonic() > deadline:
                    stats["timed_out"] = True
                    break""",
    """            # Bounded candidate chunks prevent a giant Python list and
            # ensure the time budget remains effective under dense data.
            for start in range(0, len(counts), 32768):
                if _time.monotonic() > deadline:
                    stats["timed_out"] = True
                    break
                block = counts[start:start + 32768]
                for rel in np.flatnonzero(block >= threshold):
                    i = start + int(rel)
                    if _time.monotonic() > deadline:
                        stats["timed_out"] = True
                        break
                    stats[key] += 1
                    _classify(i)
                    v = _validate_table_window(proc, memory, base, i)
                    if v > best_v:
                        best_v = v
                        best_i = i
                if stats["timed_out"]:
                    break""",
    "bounded numpy candidate iterator")
offsets.write_text(s,encoding="utf-8")

r=reader.read_text(encoding="utf-8")
r=once(r, "import struct\nimport time\n", "import struct\nimport time\nimport threading\n", "reader lock import")
r=once(r,"        self.proc = proc\n", "        self.proc = proc\n        self._kvhao_scan_lock = threading.Lock()\n", "reader scan lock")
r=once(r,
    "    def discover(self, fast: bool = False) -> int:",
    """    def discover(self, fast: bool = False) -> int:
        # Manual Diagnostics and automatic discovery must never concurrently
        # enumerate/scan the same process or mutate the offset base.
        lock = getattr(self, "_kvhao_scan_lock", None)
        if lock is None:  # also supports pure unit tests without __init__
            return self._discover_locked(fast)
        with lock:
            return self._discover_locked(fast)

    def _discover_locked(self, fast: bool = False) -> int:""",
    "serialize manual and auto structural discovery")
r=once(r,
    """        if fast:
            # Scan plausible game-bearing images only. An explicit Diagnostics
            # scan still uses the original exhaustive scan for other builds.
            preferred = [m for m in modules if m[2].casefold().endswith(
                ("d2r.exe", "d2rloader.exe", "d2rcore.dll"))]
            modules = preferred or [(
                self.proc.module_base, self.proc.module_size, self.proc.module_name)]
        base, off = discover_unit_table(
            self.proc, modules=modules, stats=stats,
            time_budget=8.0 if fast else 90.0)""",
    """        if fast:
            # First pass: allow enough time for the actual D2RLoader image,
            # not just 4 seconds per module as in v11.
            primary = [m for m in modules if m[2].casefold().endswith(
                ("d2r.exe", "d2rloader.exe", "d2rcore.dll"))]
            if not primary:
                primary = [(
                    self.proc.module_base, self.proc.module_size,
                    self.proc.module_name)]
            base, off = discover_unit_table(
                self.proc, modules=primary, stats=stats, time_budget=25.0)
            if not base:
                # The game image can be hosted in another substantial module.
                # Exclude tiny system DLLs from the AUTOMATIC fallback to
                # keep cost bounded. Manual Diagnostics still scans all.
                secondary = [m for m in modules
                             if m not in primary and m[1] >= 2 * 1024 * 1024]
                if secondary:
                    phase2 = {}
                    base, off = discover_unit_table(
                        self.proc, modules=secondary,
                        stats=phase2, time_budget=20.0)
                    stats.setdefault("by_module", {}).update(
                        phase2.get("by_module", {}))
                    stats["secondary_modules"] = len(secondary)
                    stats["secondary_timed_out"] = phase2.get("timed_out", False)
        else:
            base, off = discover_unit_table(
                self.proc, modules=modules, stats=stats, time_budget=90.0)""",
    "multi-stage offset search with broader module fallback")
r=once(r,
    """            if self.proc.module_base != base:
                self.proc.module_base = base
                self.offsets = calculate_offsets(self.proc)""",
    """            if self.proc.module_base != base:
                # Synchronize all module metadata before re-scanning byte
                # signatures. v11 only switched base, leaving the old size.
                match = next((m for m in modules if m[0] == base), None)
                self.proc.module_base = base
                if match is not None:
                    self.proc.module_size = match[1]
                    self.proc.module_name = match[2]
                self.offsets = calculate_offsets(self.proc)""",
    "fix module base/size mismatch after discovery")
reader.write_text(r,encoding="utf-8")

a=app.read_text(encoding="utf-8")
a=once(a,
    """        hp = max(0, min(100, snap.hp_percent))
        mp = max(0, min(100, snap.mana_percent))""",
    """        # With unresolved offsets the snapshot defaults can report 100%
        # for HP=0/0. Never paint full green bars for unreadable game data.
        hp = max(0, min(100, snap.hp_percent)) if snap.in_game and snap.max_hp > 0 else 0
        mp = max(0, min(100, snap.mana_percent)) if snap.in_game and snap.max_mana > 0 else 0""",
    "do not show full bars with unknown health/mana")
a=once(a,
    '        self.hp_read.configure(text=f"{snap.hp}/{snap.max_hp}  ({hp}%)")',
    '        self.hp_read.configure(text=f"{snap.hp}/{snap.max_hp}  ({hp}%)" if snap.max_hp > 0 else "Chưa đọc được HP")',
    "HP unknown display")
a=once(a,
    '        self.mp_read.configure(text=f"{snap.mana}/{snap.max_mana}  ({mp}%)")',
    '        self.mp_read.configure(text=f"{snap.mana}/{snap.max_mana}  ({mp}%)" if snap.max_mana > 0 else "Chưa đọc được MP")',
    "MP unknown display")
app.write_text(a,encoding="utf-8")
print("KVHao v12: UnitTable scan speed, module fallback, synchronized module metadata; "
      "50ms critical vitals and all fail-safe potion guards preserved")
