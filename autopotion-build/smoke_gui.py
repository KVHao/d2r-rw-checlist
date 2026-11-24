"""Smoke-test actual Windows Tk UI creation; requires a real display."""
from pathlib import Path
import sys

src = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(src))
from ui.app import MainApp

app = MainApp()
try:
    app.update_idletasks()
    app.update()
    assert app.title().startswith("KVHao AutoPotion"), app.title()
    assert app._profile_entry.winfo_exists(), "Profile input widget missing"
    assert app.tabs.winfo_exists(), "Tab view missing"
    assert app._loader_check_btn.winfo_exists(), "Loader diagnostic button missing"
    assert app._kvhao_copy_diag_btn.winfo_exists(), "Diagnostic copy button missing"
    app._kvhao_copy_diagnostics()
    assert "Quét offset" in app.diag_hint.cget("text"), "Empty diagnostic text should not claim copied"
    from d2r.process import find_d2rloader_processes, find_d2r_processes
    assert isinstance(find_d2rloader_processes(), list), "Loader discovery must return list"
    assert isinstance(find_d2r_processes(), list), "Game discovery must return list"
    if not find_d2r_processes():
        app._check_loader_connection()
        diag = app.diag_box.get("1.0", "end")
        assert "D2RLoader.exe" in diag, "Loader process explanation missing"
        assert "D2R.exe" in diag, "Game process explanation missing"
    assert app.reconnect_btn.cget("text") == "Kết nối", "Connect label not translated"
    assert app.hp_name.cget("text") == "Máu", "Health label not translated"
    assert app.mp_name.cget("text") == "Năng lượng", "Mana label not translated"
    assert app._profile_entry.cget("placeholder_text") == "tên mới", "Profile placeholder not translated"
    tabs = app.tabs._segmented_button._buttons_dict
    assert tabs["Dashboard"].cget("text") == "Tổng quan", "Dashboard tab label not translated"
    assert app.tabs.tab("Dashboard").winfo_exists(), "Internal English tab name must remain usable"
    print(f"WINDOW_SMOKE_OK {app.title()}", flush=True)
finally:
    app.destroy()
