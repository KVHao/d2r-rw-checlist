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
