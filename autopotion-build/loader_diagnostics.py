# -*- coding: utf-8 -*-
"""KVHao v9 — D2RLoader launch diagnostics, no loader injection.

Keeps the working v7/v8 executable, Win32 memory reader and potion logic.
Only improves game-PID selection and connection diagnostics.
"""
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve()
proc=root/"d2r"/"process.py"
app=root/"ui"/"app.py"
if not proc.is_file() or not app.is_file():
    raise RuntimeError("Upstream files missing")

def replace_once(src, before, after, label):
    hits=src.count(before)
    if hits!=1:
        raise RuntimeError(f"{label}: expected one anchor, found {hits}")
    return src.replace(before,after,1)

p=proc.read_text(encoding="utf-8")
p=replace_once(p,
    "    return [pid for pid, _ in sorted(found.items(), key=lambda kv: kv[1])]",
    """    # Prefer an explicitly chosen live D2R PID, then the focused game window.
    # Never attach to D2RLoader.exe itself: the memory reader needs D2R.exe.
    import os
    ordered = [pid for pid, _ in sorted(found.items(), key=lambda kv: kv[1])]
    forced = os.environ.get("D2R_AUTOPOTION_PID", "").strip()
    if forced.isdecimal() and int(forced) in ordered:
        pid = int(forced)
        ordered.remove(pid)
        return [pid] + ordered
    try:
        hwnd = user32.GetForegroundWindow()
        foreground_pid = wt.DWORD(0)
        if hwnd:
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(foreground_pid))
            if foreground_pid.value in ordered:
                pid = foreground_pid.value
                ordered.remove(pid)
                return [pid] + ordered
    except Exception:
        pass
    return ordered""",
    "game PID priority")
p=replace_once(p,
    "\ndef get_process_name(pid: int) -> str:",
    """
def find_d2rloader_processes() -> list[int]:
    \"\"\"Report launcher presence only; it isn't a supported game memory target.\"\"\"
    found = []
    for pe in _process_snapshot():
        name = pe.szExeFile.decode("utf-8", "ignore").rstrip("\\x00")
        if name.casefold() == "d2rloader.exe":
            found.append(pe.th32ProcessID)
    return sorted(set(found))


def get_process_name(pid: int) -> str:""",
    "loader discovery")
p=replace_once(p,
    '                last_err = f"Could not open process (pid {cand})."',
    '                last_err = (f"Cannot open D2R.exe PID {cand}: Win32 error "\n'
    '                            f"{ctypes.get_last_error()}. Run AutoPotion with the same "\n'
    '                            f"Windows privileges as the game and inspect Windows permissions.")',
    "specific access error")
proc.write_text(p,encoding="utf-8")

a=app.read_text(encoding="utf-8")
a=replace_once(a,
    "from d2r.process import Process, ProcessNotFound, find_d2r_processes",
    "from d2r.process import Process, ProcessNotFound, find_d2r_processes, find_d2rloader_processes",
    "process imports")
a=replace_once(a,
    '        self.diag_hint = ctk.CTkLabel(top, text="", text_color="gray60")',
    '''        self._loader_check_btn = ctk.CTkButton(
            top, text="Kiểm tra D2RLoader", width=158, height=28,
            command=self._check_loader_connection)
        self._loader_check_btn.pack(side="left", padx=(10, 0))
        self.diag_hint = ctk.CTkLabel(top, text="", text_color="gray60")''',
    "diagnostics button")
a=replace_once(a,
    '    def _try_connect(self):',
    '''    def _check_loader_connection(self):
        """Explain actual launcher, game PID, access and offset status."""
        loaders = find_d2rloader_processes()
        games = find_d2r_processes()
        lines = [
            "=== KIỂM TRA D2RLOADER / AUTOPOTION ===",
            ("D2RLoader.exe: đang chạy (PID " + ", ".join(map(str, loaders)) + ")")
                if loaders else "D2RLoader.exe: chưa thấy tiến trình",
            ("D2R.exe: đang chạy (PID " + ", ".join(map(str, games)) + ")")
                if games else "D2R.exe: chưa thấy tiến trình game",
        ]
        if not games:
            lines.append(
                "Chưa có D2R.exe. Mở game thực sự từ D2RLoader và vào nhân vật, "
                "sau đó kiểm tra lại. Không thể đọc HP/Mana từ launcher.")
        else:
            try:
                probe = Process.attach()
                lines.append(
                    f"Đọc tiến trình: OK, PID {probe.pid}, "
                    f"module={probe.module_name}, size={probe.module_size}")
                lines.append(
                    "Offset: " + ("đã nhận diện" if self.reader and self.reader.offsets.ok
                                      and self.proc and self.proc.pid == probe.pid
                                      else "chưa xác nhận: vào game rồi bấm Quét offset"))
            except Exception as exc:
                lines.append(f"Không thể kết nối D2R.exe: {exc}")
        lines.append(
            "Nếu D2R.exe đang chạy mà không đọc được: thử mở ứng dụng "
            "cùng quyền Administrator với game, không tự động bật uống bình.")
        message = "\\n".join(lines)
        self._emit_log(message, "info")
        self.diag_box.configure(state="normal")
        self.diag_box.delete("1.0", "end")
        self.diag_box.insert("end", message)
        self.diag_box.configure(state="disabled")
        self.diag_hint.configure(text="Đã kiểm tra: xem kết quả bên dưới", text_color=GOOD)

    def _try_connect(self):''',
    "loader check method")
a=replace_once(a,
    '''            if not find_d2r_processes():
                self._set_status("Game not found", WARN)
                return''',
    '''            if not find_d2r_processes():
                if find_d2rloader_processes():
                    self._set_status("Chờ D2R.exe", WARN)
                else:
                    self._set_status("Game not found", WARN)
                return''',
    "loader waiting status")
a=replace_once(a,
    '''        except ProcessNotFound:
            self._set_status("Game not found", WARN)''',
    '''        except ProcessNotFound as exc:
            self._set_status("Không mở được D2R.exe", DANGER)
            self.on_event(m.GameEvent(
                kind="error", message=f"Không thể kết nối D2R.exe: {exc}"))''',
    "access exception error")
a=replace_once(a,
    '''                    else:
                        self._set_status("Game not found", WARN)
        except Exception:
            pass
        self.after(150, self._poll)''',
    '''                    else:
                        self._set_status(
                            "Chờ D2R.exe" if find_d2rloader_processes()
                            else "Game not found", WARN)
        except Exception:
            pass
        self.after(150, self._poll)''',
    "poll loader check")
app.write_text(a,encoding="utf-8")
print("KVHao v9 loader/game diagnostics patch applied")
