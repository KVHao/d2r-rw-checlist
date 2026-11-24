"""Unit checks for v11 low-overhead behavior. Requires no running game."""
from pathlib import Path
from unittest.mock import Mock, patch
from types import SimpleNamespace
import sys
root=Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root))
from d2r.reader import GameReader
from d2r.watcher import PotionWatcher
import d2r.reader as reader_mod

assert PotionWatcher.FAST_INTERVAL_SEC==0.05, "HP/MP sampling must remain 50ms"
assert PotionWatcher.FULL_INTERVAL_SEC==0.65, "full snapshot interval wrong"
r=GameReader.__new__(GameReader)
r._count_monsters=Mock(return_value=3)
with patch.object(reader_mod.time, "monotonic", side_effect=[100.0,100.1,100.3,100.5]):
    assert r.engaged_monsters_near(12)==3
    assert r.engaged_monsters_near(12)==3
    assert r.engaged_monsters_near(12)==3
    assert r.engaged_monsters_near(12)==3
assert r._count_monsters.call_count==2, "Monster cache should avoid repeated memory scans"

r.proc=SimpleNamespace(
    module_base=0x100000,
    module_size=1000,
    module_name="D2RLoader.exe",
    all_modules=[
        (0x100000, 1000, "D2RLoader.exe"),
        (0x200000, 5000, "D2RCore.dll"),
        (0x300000, 7000, "unrelated.dll"),
    ],
)
r.offsets=SimpleNamespace(struct_stats={},ok=False)
with patch("d2r.offsets.discover_unit_table",return_value=(0,0)) as discover:
    r.discover(fast=True)
    args,kwargs=discover.call_args
    assert kwargs["time_budget"]==25.0, kwargs
    assert [m[2] for m in kwargs["modules"]]==["D2RLoader.exe","D2RCore.dll"],kwargs
with patch("d2r.offsets.discover_unit_table",return_value=(0,0)) as discover:
    r.discover()
    args,kwargs=discover.call_args
    assert kwargs["time_budget"]==90.0
    assert len(kwargs["modules"])==3,kwargs
print("PERF_TEST_OK: 50ms HP/MP, 650ms inventory, 400ms monster cache, 25s primary scan")
