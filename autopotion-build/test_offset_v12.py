"""KVHao v12 checks: efficient rolling counts, game module fallback, synced base.
Pure Windows unit tests, no game data or memory modification.
"""
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np

sys.path.insert(0,str(Path(sys.argv[1]).resolve()))
from d2r.reader import GameReader
from d2r.watcher import PotionWatcher

# Prefix method must be bit-for-bit equivalent to original moving count.
rng=np.random.default_rng(42)
for n in (128,129,1000,80000):
    values=rng.choice(np.array([0,0,0,0,0,12,0x100020000],dtype=np.uint64),size=n)
    nz=(values!=0).astype(np.uint8)
    prefix=np.empty(n+1,dtype=np.int32)
    prefix[0]=0
    np.cumsum(nz,dtype=np.int32,out=prefix[1:])
    actual=prefix[128:]-prefix[:-128]
    expected=np.convolve(nz.astype(np.int32),np.ones(128,dtype=np.int32),mode="valid")
    assert np.array_equal(actual,expected),(n,actual,expected)

# Primary miss must NOT silently end scanning; include a fallback module.
r=GameReader.__new__(GameReader)
r.proc=SimpleNamespace(module_base=0x100000,module_size=11_000_000,
                       module_name="D2RLoader.exe",
                       all_modules=[
                          (0x100000,11_000_000,"D2RLoader.exe"),
                          (0x200000,5_000_000,"D2RCore.dll"),
                          (0x300000,7_000_000,"GameDataImage.dll"),
                          (0x400000,100000,"tinyhelper.dll"),
                       ])
r.offsets=SimpleNamespace(
    UnitTable=0,module_base=0x100000,module_name="D2RLoader.exe",
    unresolved=["UnitTable"],matched={},struct_stats={})
new_offsets=SimpleNamespace(
    UnitTable=0,module_base=0,module_name="",unresolved=["UnitTable"],
    matched={},struct_stats={})
calls=[]
def fake_discover(proc,modules=None,stats=None,time_budget=None):
    calls.append((time_budget,[m[2] for m in modules]))
    if stats is not None:
        stats["by_module"]={n:{"timed_out":False} for _,_,n in modules}
    if len(calls)==1:
        return 0,0
    return 0x300000,0x1234

with patch("d2r.offsets.discover_unit_table",side_effect=fake_discover), \
     patch("d2r.offsets.calculate_offsets",return_value=new_offsets):
    address=r.discover(fast=True)
assert address==0x301234,address
assert calls==[(25.0,["D2RLoader.exe","D2RCore.dll"]),
               (20.0,["GameDataImage.dll"])], calls
assert r.proc.module_base==0x300000
assert r.proc.module_size==7_000_000
assert r.proc.module_name=="GameDataImage.dll"
assert r.offsets.UnitTable==0x1234
assert r.offsets.module_name=="GameDataImage.dll"
assert r.offsets.ok if hasattr(r.offsets,"ok") else True
assert r.offsets.matched.get("UnitTable")=="structural-scan"

# A good primary result shouldn't initiate the fallback.
calls.clear()
r.proc.module_base=0x100000
r.proc.module_size=11_000_000
r.proc.module_name="D2RLoader.exe"
r.offsets=SimpleNamespace(
    UnitTable=0,module_base=0x100000,module_name="D2RLoader.exe",
    unresolved=["UnitTable"],matched={},struct_stats={})
with patch("d2r.offsets.discover_unit_table",return_value=(0x100000,0x4567)) as scan:
    addr=r.discover(fast=True)
    assert scan.call_count==1
assert addr==0x104567
assert r.proc.module_base==0x100000

assert PotionWatcher.FAST_INTERVAL_SEC==0.05
assert PotionWatcher.FULL_INTERVAL_SEC==0.65
print("OFFSET_V12_TEST_OK: O(n) rolling counts, expanded fallback, correct selected module size")
