"""Windows-only unit checks for real D2RLoader.exe process-name recognition.
No game, memory access, DLL injection, or keypresses are used.
"""
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

root=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(root))
from d2r import process as p

assert p._is_game_name("D2R.exe")
assert p._is_game_name("d2rloader.exe")
assert not p._is_game_name("unrelated-launcher.exe")
assert p.GAME_PROCESS_NAMES == ["D2R.exe", "D2RLoader.exe"]

mock_snapshot=[
    SimpleNamespace(szExeFile=b"D2RLoader.exe",th32ProcessID=23001),
    SimpleNamespace(szExeFile=b"D2R.exe",th32ProcessID=23002),
    SimpleNamespace(szExeFile=b"SomethingElse.exe",th32ProcessID=20000),
]
with patch.object(p,"_process_snapshot",return_value=mock_snapshot), \
     patch.dict(os.environ,{"D2R_AUTOPOTION_PID":"23001"}):
    assert p.find_d2rloader_processes()==[23001]
    assert p.find_d2r_processes()==[23001,23002]
with patch.object(p,"_process_snapshot",return_value=mock_snapshot), \
     patch.dict(os.environ,{"D2R_AUTOPOTION_PID":"23002"}):
    assert p.find_d2r_processes()==[23002,23001]

mock_kernel=MagicMock()
mock_kernel.OpenProcess.return_value=101
mock_modules=[
    (0x140000000,0x3000000,"D2RLoader.exe"),
    (0x7FF0000000,0x500000,"D2RCore.dll"),
]
with patch.object(p,"kernel32",mock_kernel), \
     patch.object(p,"get_process_modules",return_value=mock_modules), \
     patch.object(p,"get_process_name",return_value="D2RLoader.exe"):
    target=p.Process.attach(pid=23001)
    assert target.pid==23001
    assert target.module_name=="D2RLoader.exe"
    assert target.module_base==0x140000000
    assert target.module_size==0x3000000
    del target
print("PROCESS_TEST_OK: both D2R.exe and D2RLoader.exe accepted as game image")
