# -*- coding: utf-8 -*-
"""Safe compile-time UI-only localization. Does not monkey-patch CustomTkinter.

Transforms only display arguments in ui/app.py and ui/widgets.py. Internal
menu values, config keys, class names and callbacks remain English/unmodified.
"""
import ast
from pathlib import Path
import shutil
import sys

root = Path(sys.argv[1]).resolve()
out_module = Path(__file__).with_name("kvhao_vi.py")
ui = root / "ui"
if not (out_module.is_file() and (ui / "app.py").is_file()):
    raise RuntimeError("Localization files missing")
shutil.copy2(out_module, ui / "kvhao_vi.py")

KW_WIDGETS = {"CTkLabel", "CTkButton", "CTkCheckBox",
              "CTkSwitch", "CTkRadioButton", "CTkEntry"}
HELPERS = {"attach_tooltip", "heading", "hint", "labeled_slider", "stat_bar"}

def localize(path):
    src = path.read_bytes()
    tree = ast.parse(src, filename=str(path))
    line_offsets = [0]
    for line in src.splitlines(keepends=True):
        line_offsets.append(line_offsets[-1] + len(line))
    changes = []
    def wrap(node):
        s = line_offsets[node.lineno - 1] + node.col_offset
        e = line_offsets[node.end_lineno - 1] + node.end_col_offset
        if s >= e or e > len(src): raise RuntimeError("Invalid source offset")
        changes.append((s, e))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute):
            continue
        is_ctk_widget = (isinstance(func.value, ast.Name)
                         and func.value.id == "ctk"
                         and func.attr in KW_WIDGETS)
        is_configure = func.attr == "configure"
        if is_ctk_widget or is_configure:
            for kw in node.keywords:
                if kw.arg == "text" or (is_ctk_widget and kw.arg == "placeholder_text"):
                    wrap(kw.value)
        is_helper = (isinstance(func.value, ast.Name)
                     and func.value.id == "w"
                     and func.attr in HELPERS)
        if is_helper and len(node.args) >= 2:
            wrap(node.args[1])
    if len(changes) < (65 if path.name == "app.py" else 4):
        raise RuntimeError(f"Unexpected number of display strings: {path} {len(changes)}")
    changes.sort(reverse=True)
    for s, e in changes:
        src = src[:s] + b"_kvhao_tr(" + src[s:e] + b")" + src[e:]
    future = b"from __future__ import annotations\n"
    if src.count(future) != 1: raise RuntimeError("Missing known future import")
    src = src.replace(future, future + b"\nfrom ui.kvhao_vi import tr as _kvhao_tr\n", 1)
    path.write_bytes(src)
    print(f"Translated display nodes: {path.name}: {len(changes)}")

localize(ui / "app.py")
localize(ui / "widgets.py")

# Change tab presentation labels only, retaining original tab identifiers
# used throughout the code for navigation & callbacks.
app_file = ui / "app.py"
text = app_file.read_text(encoding="utf-8")
anchor = '        self._build_log(self.tabs.tab("Log"))\n'
if text.count(anchor) != 1:
    raise RuntimeError("Cannot find stable tab rendering anchor")
tab_labels = """
        # KVHao: display-only tab captions; keep internal English tab names.
        _vi_tabs = {
            "Dashboard": "Tổng quan", "Triggers": "Ngưỡng uống",
            "Keys": "Phím tắt", "Calibrate": "Hiệu chỉnh",
            "Diagnostics": "Chẩn đoán", "Log": "Nhật ký",
        }
        _segmented = getattr(self.tabs, "_segmented_button", None)
        _buttons = getattr(_segmented, "_buttons_dict", {})
        for _tab_name, _vi_caption in _vi_tabs.items():
            _button = _buttons.get(_tab_name)
            if _button is not None:
                _button.configure(text=_vi_caption)
"""
text = text.replace(anchor, anchor + tab_labels, 1)
app_file.write_text(text, encoding="utf-8")
print("Localization applied without class or widget monkey-patching")
