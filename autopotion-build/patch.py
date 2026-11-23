# -*- coding: utf-8 -*-
"""Build-only KVHao patches. No injection into game or launcher."""
from pathlib import Path
import shutil
import sys

root=Path(sys.argv[1]).resolve()
main=root/"main.py"
ui=root/"ui"
watcher=root/"d2r"/"watcher.py"
source=Path(__file__).resolve().parent/"kvhao_locale.py"

if not all(p.exists() for p in (main,ui,watcher,source)):
    raise RuntimeError("Missing upstream files or KVHao locale")
text=main.read_text(encoding="utf-8")
anchor="        from ui.app import run"
assert text.count(anchor)==1, "Unknown upstream main.py; refusing unsafe patch"
text=text.replace(anchor,
    "        from ui import kvhao_locale\n"
    "        kvhao_locale.install()\n"+anchor,1)
main.write_text(text,encoding="utf-8")
shutil.copy2(source,ui/"kvhao_locale.py")

text=watcher.read_text(encoding="utf-8")
anchor="        if not snap.in_game or not snap.alive:\n            return False"
assert text.count(anchor)==1, "Unknown upstream watcher; refusing unsafe patch"
guard=(
    "        # KVHao fail-closed: do not press keys when game data is invalid.\n"
    "        if (not self.reader.offsets.ok or not snap.potion_counts.ok\n"
    "                or snap.error or snap.max_hp <= 0 or snap.max_mana <= 0\n"
    "                or snap.hp > snap.max_hp or snap.mana > snap.max_mana):\n"
    "            return False\n"
)
watcher.write_text(text.replace(anchor,guard+anchor,1),encoding="utf-8")
print("KVHao Infernal/RotW localization and guard patch OK")
