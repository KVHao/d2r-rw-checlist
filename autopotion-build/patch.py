# -*- coding: utf-8 -*-
"""KVHao AutoPotion - Infernal/RotW compatibility patch.
Do not monkey-patch CustomTkinter or inject anything into D2RLoader.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
app = root / "ui" / "app.py"
watcher = root / "d2r" / "watcher.py"
process = root / "d2r" / "process.py"
if not all(path.is_file() for path in (app, watcher, process)):
    raise RuntimeError("Upstream files missing; aborting")

# Preserve original interface functionality in English. Only rebrand two
# literal UI strings; modifying widget classes caused the v1 startup crash.
text = app.read_text(encoding="utf-8")
replacements = (
    ('self.title(f"D2R Infernal Auto Potion v{__version__}")',
     'self.title(f"KVHao AutoPotion v{__version__}")'),
    ('text="⚔  D2R Infernal Auto Potion"',
     'text="⚔  KVHao AutoPotion"'),
)
for before, after in replacements:
    if text.count(before) != 1:
        raise RuntimeError(f"Upstream app changed: expected exactly one {before!r}")
    text = text.replace(before, after, 1)
app.write_text(text, encoding="utf-8")

# The external companion attaches to D2R.exe, which remains the game process
# when launched via D2RLoader. Do not attempt to load into d2rloader itself.
txt = process.read_text(encoding="utf-8")
if 'GAME_PROCESS_NAMES = ["D2R.exe"]' not in txt:
    raise RuntimeError("Unknown game process detection; aborting")

# Preserve fail-closed guard to prevent automated keypresses on invalid reads.
text = watcher.read_text(encoding="utf-8")
anchor = "        if not snap.in_game or not snap.alive:\n            return False"
if text.count(anchor) != 1:
    raise RuntimeError("Unknown watcher structure; aborting")
guard = (
    "        # KVHao safety: stop output if the memory readings are invalid.\n"
    "        if (not self.reader.offsets.ok or not snap.potion_counts.ok\n"
    "                or snap.error or snap.max_hp <= 0 or snap.max_mana <= 0\n"
    "                or snap.hp > snap.max_hp or snap.mana > snap.max_mana):\n"
    "            return False\n"
)
watcher.write_text(text.replace(anchor, guard + anchor, 1), encoding="utf-8")
print("KVHao: original English UI retained, D2R.exe detection confirmed, guard applied")
