# -*- coding: utf-8 -*-
"""KVHao AutoPotion Vietnamese UI. Upstream author: DavidPinto (MIT)."""
import functools
import re

VI = {
    "Dashboard":"Tổng quan", "Triggers":"Ngưỡng uống", "Keys":"Phím tắt",
    "Calibrate":"Hiệu chỉnh", "Diagnostics":"Chẩn đoán", "Log":"Nhật ký",
    "⚔  D2R Infernal Auto Potion":"⚔  KVHao AutoPotion",
    "D2R Infernal Auto Potion":"KVHao AutoPotion",
    "Connect":"Kết nối", "Reconnect":"Kết nối lại",
    "Starting…":"Đang khởi động…", "DISABLED":"ĐÃ TẮT",
    "● ENABLED":"● ĐANG BẬT", "Hotkey: off":"Phím bật/tắt: chưa đặt",
    "Profile:":"Cấu hình:", "new name":"tên mới",
    "Save":"Lưu", "Load":"Nạp", "Delete":"Xóa",
    "No character":"Chưa có nhân vật", "Not in game":"Chưa vào game",
    "In game":"Đang trong game", "Health":"Máu", "Mana":"Năng lượng",
    "Mercenary":"Đệ tử", "no merc":"chưa có đệ",
    "Potion supply":"Số bình thuốc",
    "Belt: unknown   ·   Inventory: unknown":"Dây đai: chưa rõ   ·   Túi đồ: chưa rõ",
    "Belt: unknown   ·   Inventory: unknown (read in-game)":"Dây đai: chưa rõ   ·   Túi đồ: chưa rõ (xem trong game)",
    "Session":"Phiên chơi", "Potions used: 0":"Đã uống: 0 bình",
    "Manual max (0 = auto):":"Giới hạn thủ công (0 = tự động):",
    "Merc":"Đệ", "Apply":"Áp dụng",
    "Calibration saved (0 = auto).":"Đã lưu hiệu chỉnh (0 = tự động).",
    "Presets":"Thiết lập nhanh", "Apply preset":"Áp dụng mẫu",
    "Trigger thresholds (%)":"Ngưỡng kích hoạt (%)",
    "Health potion at HP ≤":"Uống bình máu khi HP ≤",
    "Mana potion at MP ≤":"Uống bình mana khi MP ≤",
    "Rejuv at HP ≤":"Uống bình hồi phục khi HP ≤",
    "Rejuv at MP <":"Uống bình hồi phục khi MP <",
    "Merc health at HP ≤":"Cho đệ uống máu khi HP ≤",
    "Merc rejuv at HP ≤":"Cho đệ uống hồi phục khi HP ≤",
    "Safety margin (%)":"Biên an toàn (%)",
    "Smart behavior":"Hành vi thông minh",
    "Predictive drinking (drink slightly before a bar empties)":"Uống sớm khi dự đoán máu/mana sắp cạn",
    "Reach buried rejuv (emergency; wastes potions)":"Lấy bình hồi phục nằm sâu (khẩn cấp, tốn bình)",
    "Reset to defaults":"Khôi phục mặc định",
    "Belt columns & hotkeys":"Cột dây đai và phím tắt",
    "Gamepad support":"Hỗ trợ tay cầm",
    "Use gamepad D-pad for belt keys (real gamepad input)":"Dùng D-pad tay cầm để uống bình",
    "Mercenary potion modifier":"Phím bổ trợ cho đệ",
    "Feed-to-merc modifier":"Phím kết hợp cho đệ uống bình",
    "Give potions to the mercenary":"Tự cho đệ uống bình",
    "General options":"Tùy chọn chung",
    "Auto-focus game window before pressing keys":"Tự chuyển vào cửa sổ game trước khi gửi phím",
    "Saved potion codes":"Bộ mã bình đã lưu", "Active profile:":"Cấu hình đang dùng:",
    "Use":"Sử dụng", "Teach the app your potions":"Nhận dạng bình thuốc",
    "Potion in the belt corners:":"Loại bình ở bốn góc dây đai:",
    "Scan belt corners":"Quét bốn góc dây đai",
    "Merc hireling txtFileNo(s) (optional):":"Mã txtFileNo đệ tử (tùy chọn):",
    "Learned so far":"Mã đã nhận dạng",
    "Clear calibration":"Xóa hiệu chỉnh",
    "Instructions":"Hướng dẫn",
    "Run offset scan & read test":"Quét offset và kiểm tra dữ liệu",
    "Scanning… (stay in a game, up to ~45s)":"Đang quét… (ở trong game, tối đa 45 giây)",
    "Offsets found":"Đã tìm thấy offset", "Check output":"Kiểm tra kết quả",
    "Cannot read game":"Không đọc được game",
    "Clear log":"Xóa nhật ký", "Export diagnostics":"Xuất báo cáo chẩn đoán",
    "Log cleared.":"Đã xóa nhật ký",
    "Looking for D2R…":"Đang tìm D2R…", "Game not found":"Không tìm thấy game",
    "Attach failed":"Kết nối thất bại", "Connected":"Đã kết nối",
    "Searching offsets…":"Đang tìm offset…", "Offsets unresolved":"Chưa tìm thấy offset",
    "Game closed":"Game đã đóng",
    "Health potion":"Bình máu", "Mana potion":"Bình mana",
    "Rejuvenation":"Bình hồi phục",
    "Merc health (Shift)":"Đệ uống máu (Shift)",
    "Merc rejuv (Shift)":"Đệ uống hồi phục (Shift)",
    "Leveling":"Luyện cấp", "Boss farming":"Săn boss",
    "Conservative":"An toàn", "Mana-heavy":"Ưu tiên mana",
    "Minor Health potion":"Bình máu cấp 1",
    "Light Health potion":"Bình máu cấp 2",
    "Healing Potion":"Bình máu cấp 3",
    "Greater Health potion":"Bình máu cấp 4",
    "Super Health potion":"Bình máu cấp 5",
    "Minor Mana potion":"Bình mana cấp 1",
    "Light Mana potion":"Bình mana cấp 2",
    "Mana Potion":"Bình mana cấp 3",
    "Greater Mana potion":"Bình mana cấp 4",
    "Super Mana potion":"Bình mana cấp 5",
    "Rejuvenation potion":"Bình hồi phục",
    "Full Rejuvenation potion":"Bình hồi phục toàn phần",
    "Antidote potion":"Bình giải độc",
    "heal":"máu", "mana":"mana", "rejuv":"hồi phục", "other":"khác",
    "antidote":"giải độc",
    "Select a saved potion-code set first.":"Chọn bộ mã bình đã lưu trước",
    "Connect to the game first, then scan.":"Kết nối game trước rồi quét",
    "Press Esc to clear":"Nhấn Esc để xóa",
    "Cannot enable: not connected / offsets unresolved. See Diagnostics.":"Không thể bật: chưa kết nối hoặc chưa có offset. Xem Chẩn đoán.",
    "Could not auto-find offsets. Open Diagnostics → Run scan while in a game.":"Không tự tìm thấy offset. Vào Chẩn đoán và quét khi đang trong game.",
    "Using built-in Infernal potion defaults.":"Đang dùng bộ mã bình Infernal mặc định.",
    "Global hotkey cleared.":"Đã xóa phím bật/tắt.",
    "No profile selected to load.":"Chưa chọn cấu hình để nạp.",
    "Enter a profile name first.":"Nhập tên cấu hình trước.",
}
MENU_KEYS = ("Leveling","Boss farming","Conservative","Mana-heavy",
             "Minor Health potion","Light Health potion","Healing Potion",
             "Greater Health potion","Super Health potion",
             "Minor Mana potion","Light Mana potion","Mana Potion",
             "Greater Mana potion","Super Mana potion",
             "Rejuvenation potion","Full Rejuvenation potion","Antidote potion")
BACK = {VI[k]:k for k in MENU_KEYS}

def tr(value):
    if not isinstance(value,str): return value
    if value in VI: return VI[value]
    if value.startswith("Belt: ") or value.startswith("Inventory: "):
        return value.replace("Belt: ","Dây đai: ",1).replace("Inventory: ","Túi đồ: ",1)
    for en, vn in (("Potions used: ","Đã uống: "),("Hotkey: ","Phím bật/tắt: "),
                   ("Scan failed: ","Quét thất bại: "),("Attach failed: ","Kết nối thất bại: ")):
        if value.startswith(en): return vn+value[len(en):]
    if value.startswith("Auto-potion enabled."): return "Đã bật AutoPotion."
    if value.startswith("Auto-potion disabled."): return "Đã tắt AutoPotion."
    if value.startswith("uptime "):
        return value.replace("uptime ","thời gian ",1).replace(" potions"," bình").replace(" errors"," lỗi")
    return re.sub(r"(?<!\w)Lvl (?=\d)","Lv ",value)

def install():
    import customtkinter as ctk
    if getattr(ctk,"_kvhao_installed",False): return
    for name in ("CTkLabel","CTkButton","CTkCheckBox","CTkSwitch","CTkRadioButton"):
        cls=getattr(ctk,name,None)
        if cls is None: continue
        old_init,old_conf=cls.__init__,cls.configure
        @functools.wraps(old_init)
        def init(self,*args,_old=old_init,**kwargs):
            if "text" in kwargs: kwargs["text"]=tr(kwargs["text"])
            return _old(self,*args,**kwargs)
        @functools.wraps(old_conf)
        def configure(self,*args,_old=old_conf,**kwargs):
            if "text" in kwargs: kwargs["text"]=tr(kwargs["text"])
            return _old(self,*args,**kwargs)
        cls.__init__,cls.configure=init,configure
    cls=ctk.CTkEntry
    old=cls.__init__
    @functools.wraps(old)
    def entry(self,*args,**kwargs):
        if "placeholder_text" in kwargs: kwargs["placeholder_text"]=tr(kwargs["placeholder_text"])
        return old(self,*args,**kwargs)
    cls.__init__=entry
    cls=ctk.CTkOptionMenu
    old_init,old_set,old_get,old_conf=cls.__init__,cls.set,cls.get,cls.configure
    def trans_values(values): return [VI.get(v,v) for v in values]
    def wrap_cmd(cmd):
        if not callable(cmd): return cmd
        def callback(v): return cmd(BACK.get(v,v))
        return callback
    @functools.wraps(old_init)
    def menu_init(self,*args,**kwargs):
        if "values" in kwargs: kwargs["values"]=trans_values(kwargs["values"])
        if "command" in kwargs: kwargs["command"]=wrap_cmd(kwargs["command"])
        return old_init(self,*args,**kwargs)
    @functools.wraps(old_set)
    def menu_set(self,v,*args,**kwargs): return old_set(self,VI.get(v,v),*args,**kwargs)
    @functools.wraps(old_get)
    def menu_get(self,*args,**kwargs):
        v=old_get(self,*args,**kwargs)
        return BACK.get(v,v)
    @functools.wraps(old_conf)
    def menu_conf(self,*args,**kwargs):
        if "values" in kwargs: kwargs["values"]=trans_values(kwargs["values"])
        if "command" in kwargs: kwargs["command"]=wrap_cmd(kwargs["command"])
        return old_conf(self,*args,**kwargs)
    cls.__init__,cls.set,cls.get,cls.configure=menu_init,menu_set,menu_get,menu_conf
    cls=ctk.CTkTabview
    old=cls.add
    @functools.wraps(old)
    def add(self,name,*args,**kwargs):
        result=old(self,name,*args,**kwargs)
        try:
            btn=self._segmented_button._buttons_dict.get(name)
            if btn is not None: btn.configure(text=tr(name))
        except (AttributeError,KeyError): pass
        return result
    cls.add=add
    cls=ctk.CTk
    old=cls.title
    @functools.wraps(old)
    def title(self,value=None):
        if value is None:return old(self)
        if value.startswith("D2R Infernal Auto Potion"):
            value=value.replace("D2R Infernal Auto Potion","KVHao AutoPotion",1)
        return old(self,value)
    cls.title=title
    ctk._kvhao_installed=True
