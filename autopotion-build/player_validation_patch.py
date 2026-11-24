# -*- coding: utf-8 -*-
"""KVHao v13: never mistake a game-process attach for valid character stats.

Root issue: Offsets.ok only tests UnitTable != 0; v12 could read a false-positive
table and show Amazon Lv0 / 0:1 HP, MP and an invalid character name.
This patch fails closed and adds raw-structure diagnostics. It cannot assume
the correct offsets for an untested D2RLoader game build.
"""
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve()
reader=root/"d2r"/"reader.py"
watcher=root/"d2r"/"watcher.py"
app=root/"ui"/"app.py"

def change(s, before, after, label):
    n=s.count(before)
    if n != 1: raise RuntimeError(f"{label}: expected 1 anchor, got {n}")
    return s.replace(before,after,1)

r=reader.read_text(encoding="utf-8")
r=change(r,
    "        self.offsets: Offsets = calculate_offsets(proc)",
    "        self._kvhao_data_valid = False\n        self.offsets: Offsets = calculate_offsets(proc)",
    "initialize verified-character flag")
r=change(r,
    "    def _unit_table_looks_real(self) -> bool:",
    '''    @staticmethod
    def _kvhao_player_plausible(player: dict) -> bool:
        """Validate ACTUAL decoded stats before enabling any potions.

        D2RLoader/RotW may use a different in-memory layout; a valid pointer
        or module match does not imply we found the active character.
        Allow heavily modded levels/stats but disallow empty, missing, corrupt
        character identity or uninitialized vital values.
        """
        name = player.get("name")
        stats = player.get("stats") or {}
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 64:
            return False
        if not all(ch.isprintable() for ch in name) or not any(ch.isalnum() for ch in name):
            return False
        if player.get("class") not in m.CLASS:
            return False
        lv = stats.get(m.STAT["Level"], 0)
        hp = stats.get(m.STAT["Life"], -1)
        max_hp = stats.get(m.STAT["MaxLife"], 0)
        mp = stats.get(m.STAT["Mana"], -1)
        max_mp = stats.get(m.STAT["MaxMana"], 0)
        return (1 <= lv <= 2048
                and 1 <= max_hp <= 10_000_000 and 1 <= max_mp <= 10_000_000
                and 0 <= hp <= max_hp + 5000
                and 0 <= mp <= max_mp + 5000)

    def _unit_table_looks_real(self) -> bool:''',
    "validated player identity helper")

r=change(r,
    '''            p = self._read_player(unit)
            stats = p["stats"]
            self.codes.player_class = p["class"]
            life = stats.get(m.STAT["Life"], 0)''',
    '''            p = self._read_player(unit)
            self._kvhao_data_valid = self._kvhao_player_plausible(p)
            if not self._kvhao_data_valid:
                snap.error = ("INVALID_PLAYER_DATA: invalid character name, level or "
                              "HP/MP read; current D2RLoader structure/UnitTable "
                              "not verified. Open Diagnostics and run offset scan.")
                snap.in_game = False
                return snap
            stats = p["stats"]
            self.codes.player_class = p["class"]
            life = stats.get(m.STAT["Life"], 0)''',
    "fast path player validation")
r=change(r,
    '''            p = self._read_player(unit)
            stats = p["stats"]
            # Restore amounts are class-dependent''',
    '''            p = self._read_player(unit)
            self._kvhao_data_valid = self._kvhao_player_plausible(p)
            if not self._kvhao_data_valid:
                snap.error = ("INVALID_PLAYER_DATA: invalid character name, level or "
                              "HP/MP read; current D2RLoader structure/UnitTable "
                              "not verified. Open Diagnostics and run offset scan.")
                snap.in_game = False
                return snap
            stats = p["stats"]
            # Restore amounts are class-dependent''',
    "full path player validation")
r=change(r,
    '''            p = self._read_player(unit)
            stats = p["stats"]
            life = stats.get(m.STAT["Life"], 0)''',
    '''            p = self._read_player(unit)
            stats = p["stats"]
            lines.append("")
            lines.append("=== KVHao v13 raw player data (for offset diagnosis) ===")
            slex = self.proc.read_ptr(unit + m.UNIT_OFFSET_STATSLISTEX)
            unit_data = self.proc.read_ptr(unit + m.UNIT_OFFSET_UNIT_DATA)
            lines.append(f"  unit addr   : 0x{unit:X}")
            lines.append(f"  unit type   : {self.proc.read_u32(unit)}")
            lines.append(f"  class raw   : {self.proc.read_u32(unit + m.UNIT_OFFSET_TXTFILE)}")
            lines.append(f"  data ptr    : 0x{unit_data:X}")
            lines.append(f"  statlist ptr: 0x{slex:X}")
            lines.append(f"  stat ptr    : 0x{self.proc.read_ptr(slex + m.STATSLIST_STAT_PTR):X}" if slex else "  stat ptr    : 0")
            lines.append(f"  stat count  : {self.proc.read_ptr(slex + m.STATSLIST_STAT_COUNT)}" if slex else "  stat count  : 0")
            lines.append(f"  stat IDs    : {sorted(stats.keys())[:32]}")
            lines.append(f"  valid char  : {self._kvhao_player_plausible(p)}")
            lines.append("  NOTE: address/module match alone is not character validation.")
            life = stats.get(m.STAT["Life"], 0)''',
    "raw stat structure diagnostics")
reader.write_text(r,encoding="utf-8")

w=watcher.read_text(encoding="utf-8")
w=change(w,
    '''        if (not self.reader.offsets.ok or not snap.potion_counts.ok''',
    '''        if (not getattr(self.reader, "_kvhao_data_valid", False)
                or not self.reader.offsets.ok or not snap.potion_counts.ok''',
    "fail-closed verified player guard")
watcher.write_text(w,encoding="utf-8")

a=app.read_text(encoding="utf-8")
a=change(a,
    '        self._shown_errors: set[str] = set()',
    '        self._shown_errors: set[str] = set()\n        self._kvhao_last_data_status = None',
    "one-time status update")
a=change(a,
    '''            if reader.offsets.ok:
                self._set_status("Connected", GOOD)''',
    '''            if reader.offsets.ok:
                self._set_status("Đang xác minh nhân vật…", WARN)''',
    "do not claim connected from offset-only")
a=change(a,
    '''        else:
            self.char_label.configure(text="No character")
            self.state_label.configure(text="Not in game", text_color="gray60")

        # With unresolved offsets''',
    '''        else:
            if snap.error and "INVALID_PLAYER_DATA" in snap.error:
                self.char_label.configure(text="Chưa xác minh được nhân vật")
                self.state_label.configure(
                    text="Dữ liệu HP/MP hoặc level không hợp lệ — xem Chẩn đoán",
                    text_color="#f2994a")
            else:
                self.char_label.configure(text="No character")
                self.state_label.configure(text="Not in game", text_color="gray60")

        # With unresolved offsets''',
    "show invalid data instead of fake class")
a=change(a,
    '        self._loader_check_btn.pack(side="left", padx=(10, 0))',
    '''        self._loader_check_btn.pack(side="left", padx=(10, 0))
        self._kvhao_copy_diag_btn = ctk.CTkButton(
            top, text="Sao chép báo cáo", width=130, height=28,
            command=self._kvhao_copy_diagnostics)
        self._kvhao_copy_diag_btn.pack(side="left", padx=(8, 0))''',
    "copy diagnostic button")
a=change(a,
    '    def _run_scan(self):',
    '''    def _kvhao_copy_diagnostics(self):
        """Copy diagnostic report for troubleshooting the actual game build."""
        text = self.diag_box.get("1.0", "end").strip()
        if not text:
            self.diag_hint.configure(
                text="Chạy Quét offset trước khi sao chép", text_color=WARN)
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        self.diag_hint.configure(text="Đã sao chép báo cáo", text_color=GOOD)

    def _run_scan(self):''',
    "copy diagnostic command")
a=change(a,
    '''                    self._update_dashboard(snap)
                    if snap.error and snap.error not in self._shown_errors:''',
    '''                    self._update_dashboard(snap)
                    # A found process or hash-table address is not a verified
                    # character. Only show green when real vitals were decoded.
                    if snap.error and "INVALID_PLAYER_DATA" in snap.error:
                        status = ("Dữ liệu sai / kiểm tra offset", WARN)
                    elif snap.in_game and getattr(self.reader, "_kvhao_data_valid", False):
                        status = ("Đã kết nối", GOOD)
                    elif self.reader.offsets.ok:
                        status = ("Đang chờ dữ liệu nhân vật", WARN)
                    else:
                        status = None
                    if status is not None and status != self._kvhao_last_data_status:
                        self._kvhao_last_data_status = status
                        self._set_status(*status)
                    if snap.error and snap.error not in self._shown_errors:''',
    "status requires character validation")
a=change(a,
    '''        if off:
            self._set_status("Connected", GOOD)
            self.on_event(m.GameEvent(kind="info",
                          message=f"Resolved UnitTable offset structurally at 0x{off:X}."))''',
    '''        if off:
            self._set_status("Đang xác minh dữ liệu nhân vật", WARN)
            self.on_event(m.GameEvent(kind="info",
                          message=f"Found potential UnitTable at 0x{off:X}; validating character."))''',
    "do not mark unverified UnitTable green")
a=change(a,
    '''        if found:
            self._set_status("Connected", GOOD)
            self.diag_hint.configure(text="Offsets found", text_color=GOOD)''',
    '''        if found:
            verified = bool(self.reader and getattr(self.reader, "_kvhao_data_valid", False))
            self._set_status("Đã kết nối" if verified else "Chưa xác minh nhân vật",
                             GOOD if verified else WARN)
            self.diag_hint.configure(
                text="Đã xác minh nhân vật" if verified else "Offset tìm thấy, dữ liệu cần kiểm tra",
                text_color=GOOD if verified else WARN)''',
    "diagnostics must not mark bad stats connected")
app.write_text(a,encoding="utf-8")
print("KVHao v13: runtime player sanity, fail-closed status, and raw-stat diagnostic report installed")
