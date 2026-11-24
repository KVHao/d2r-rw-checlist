# -*- coding: utf-8 -*-
"""Fix D2RLoader game-as-process hosting (KVHao v10).

D2RLoader can be the actual game process image, not merely an external launcher.
Do not add DLL injection, memory writes, or any change to potion action logic.
Apply only after KVHao v9 diagnostics patch; fail on upstream drift.
"""
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve()
process=root/"d2r"/"process.py"
reader=root/"d2r"/"reader.py"
app=root/"ui"/"app.py"

def once(s, before, after, label):
    found=s.count(before)
    if found!=1:
        raise RuntimeError(f"{label}: expected 1 occurrence, found {found}")
    return s.replace(before, after, 1)

p=process.read_text(encoding="utf-8")
p=once(p,
    'GAME_PROCESS_NAMES = ["D2R.exe"]',
    'GAME_PROCESS_NAMES = ["D2R.exe", "D2RLoader.exe"]',
    "supported game process names")
p=once(p,
    '# The game process is always D2R.exe.  "Infernal Edition" is a D2R client\n'
    '# build and mod managers (D2RMM) inject INTO that process — they are not the\n'
    '# game themselves and must never be attached to.',
    '# The live game can run as D2R.exe or as D2RLoader.exe (native loader).\n'
    '# Attach only to an enumerated game image within its owning process.\n'
    '# Never attempt to attach to arbitrary third-party launcher windows.',
    "game process comment")
p=once(p,
    '    """Report launcher presence only; it isn\'t a supported game memory target."""',
    '    """Report D2RLoader processes; these can host the game itself."""',
    "loader discovery docs")
p=once(p,
    '    # Never attach to D2RLoader.exe itself: the memory reader needs D2R.exe.',
    '    # D2RLoader.exe can host the game; choose a real game window where possible.',
    "process selection docs")
p=once(p,
    '                last_err = (f"Cannot open D2R.exe PID {cand}: Win32 error "',
    '                last_err = (f"Cannot open game process PID {cand}: Win32 error "',
    "access error message")
p=once(p,
    '        raise ProcessNotFound(last_err or "Could not locate the D2R.exe module.")',
    '        raise ProcessNotFound(last_err or "Could not locate a D2R.exe/D2RLoader.exe game image.")',
    "game image error")
process.write_text(p,encoding="utf-8")

r=reader.read_text(encoding="utf-8")
r=once(r,
    'if n.lower().endswith("d2r.exe")]',
    'if n.lower().endswith(("d2r.exe", "d2rloader.exe"))]',
    "diagnostic game modules")
reader.write_text(r,encoding="utf-8")

a=app.read_text(encoding="utf-8")
a=once(a,
    '("D2R.exe: đang chạy (PID " + ", ".join(map(str, games)) + ")")',
    '("Tiến trình game hỗ trợ (PID " + ", ".join(map(str, games)) + ")")',
    "diagnostic game PID")
a=once(a,
    'else "D2R.exe: chưa thấy tiến trình game",',
    'else "Chưa phát hiện tiến trình game D2R.exe / D2RLoader.exe",',
    "diagnostic no game")
a=once(a,
    '"Chưa có D2R.exe. Mở game thực sự từ D2RLoader và vào nhân vật, "',
    '"Chưa có tiến trình game hợp lệ. Mở game từ D2RLoader và vào nhân vật, "',
    "no game hint")
a=once(a,
    '"sau đó kiểm tra lại. Không thể đọc HP/Mana từ launcher.")',
    '"sau đó kiểm tra lại. Không thể đọc HP/Mana nếu game chưa vào màn chơi.")',
    "no game hint detail")
a=once(a,
    'f"Đọc tiến trình: OK, PID {probe.pid}, "',
    'f"Đọc tiến trình: OK, PID {probe.pid}, exe={get_process_name(probe.pid)}, "',
    "probe exe name")
a=once(a,
    'from d2r.process import Process, ProcessNotFound, find_d2r_processes, find_d2rloader_processes',
    'from d2r.process import Process, ProcessNotFound, find_d2r_processes, find_d2rloader_processes, get_process_name',
    "import game exe names")
a=once(a,
    'lines.append(f"Không thể kết nối D2R.exe: {exc}")',
    'lines.append(f"Không thể đọc tiến trình game: {exc}")',
    "diagnostic failure")
a=once(a,
    '"Nếu D2R.exe đang chạy mà không đọc được: thử mở ứng dụng "',
    '"Nếu tiến trình game đang chạy mà không đọc được: thử mở ứng dụng "',
    "read access hint")
a=once(a,
    'self._set_status("Chờ D2R.exe", WARN)',
    'self._set_status("Chờ game khởi động", WARN)',
    "connect wait")
a=once(a,
    '"Chờ D2R.exe" if find_d2rloader_processes()',
    '"Chờ game khởi động" if find_d2rloader_processes()',
    "poll wait")
a=once(a,
    'self._set_status("Không mở được D2R.exe", DANGER)',
    'self._set_status("Không mở được game", DANGER)',
    "connect error status")
a=once(a,
    'kind="error", message=f"Không thể kết nối D2R.exe: {exc}"',
    'kind="error", message=f"Không thể kết nối tiến trình game: {exc}"',
    "connect error logging")
a=once(a,
    'message = "\\\\n".join(lines)',
    'message = "\\n".join(lines)',
    "multiline diagnostics")
app.write_text(a,encoding="utf-8")
print("KVHao v10: native D2RLoader.exe game process recognized; UI and watcher safety retained")
