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
    print(f"WINDOW_SMOKE_OK {app.title()}", flush=True)
finally:
    app.destroy()
