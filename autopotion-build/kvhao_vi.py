# -*- coding: utf-8 -*-
"""Vietnamese display strings for KVHao AutoPotion.
Original program and internal configuration keys remain unchanged.
No monkey-patching of tkinter, widgets, or option menus.
"""
import re

LABELS = {
    "Dashboard": "Tổng quan",
    "Triggers": "Ngưỡng uống",
    "Keys": "Phím tắt",
    "Calibrate": "Hiệu chỉnh",
    "Diagnostics": "Chẩn đoán",
    "Log": "Nhật ký",
    "Health potion at HP ≤": "Uống bình máu khi HP ≤",
    "Mana potion at MP ≤": "Uống bình mana khi MP ≤",
    "Rejuv at HP ≤": "Uống hồi phục khi HP ≤",
    "Rejuv at MP <": "Uống hồi phục khi MP <",
    "Merc health at HP ≤": "Cho đệ uống máu khi HP ≤",
    "Merc rejuv at HP ≤": "Cho đệ uống hồi phục khi HP ≤",
    "Starting…": "Đang khởi động…",
    "Connect": "Kết nối",
    "Reconnect": "Kết nối lại",
    "DISABLED": "ĐÃ TẮT",
    "● ENABLED": "● ĐANG BẬT",
    "Hotkey: off": "Phím bật/tắt: chưa đặt",
    "Profile:": "Cấu hình:",
    "new name": "tên mới",
    "Save": "Lưu",
    "Load": "Nạp",
    "Delete": "Xóa",
    "No character": "Chưa có nhân vật",
    "Not in game": "Chưa vào game",
    "In game": "Đang trong game",
    "Health": "Máu",
    "Mana": "Năng lượng",
    "Mercenary": "Lính đánh thuê",
    "no merc": "Chưa có lính đánh thuê",
    "Potion supply": "Số bình thuốc",
    "Belt: unknown   ·   Inventory: unknown": "Dây đai: chưa rõ   ·   Túi đồ: chưa rõ",
    "Belt: unknown   ·   Inventory: unknown (read in-game)": "Dây đai: chưa rõ   ·   Túi đồ: chưa rõ (đọc khi vào game)",
    "Session": "Phiên chơi",
    "Potions used: 0": "Số bình đã uống: 0",
    "Manual max (0 = auto):": "Chỉ số tối đa (0 = tự động):",
    "Apply": "Áp dụng",
    "Calibration saved (0 = auto).": "Đã lưu giới hạn thủ công (0 = tự động).",
    "Presets": "Thiết lập nhanh",
    "Apply preset": "Áp dụng mẫu",
    "Trigger thresholds (%)": "Ngưỡng kích hoạt (%)",
    "Safety margin (%)": "Biên an toàn (%)",
    "Smart behavior": "Tính năng thông minh",
    "Predictive drinking (drink slightly before a bar empties)": "Dự đoán để uống bình sớm khi máu/mana sắp cạn",
    "Reach buried rejuv (emergency; wastes potions)": "Tìm bình hồi phục nằm sâu (khẩn cấp, tốn bình)",
    "Reset to defaults": "Khôi phục mặc định",
    "Belt columns & hotkeys": "Cột dây đai và phím dùng bình",
    "Gamepad support": "Hỗ trợ tay cầm",
    "Use gamepad D-pad for belt keys (real gamepad input)": "Dùng D-pad của tay cầm để uống bình",
    "Mercenary potion modifier": "Phím hỗ trợ cho lính đánh thuê",
    "Feed-to-merc modifier": "Phím cho lính đánh thuê uống bình",
    "Give potions to the mercenary": "Tự cho lính đánh thuê uống bình",
    "General options": "Tùy chọn chung",
    "Auto-focus game window before pressing keys": "Đưa cửa sổ game lên trước khi gửi phím",
    "Saved potion codes": "Bộ mã bình đã lưu",
    "Active profile:": "Cấu hình đang dùng:",
    "Use": "Sử dụng",
    "Teach the app your potions": "Nhận dạng bình thuốc",
    "Potion in the belt corners:": "Bình đặt ở bốn góc dây đai:",
    "Scan belt corners": "Quét bốn góc dây đai",
    "Merc hireling txtFileNo(s) (optional):": "Mã lính đánh thuê txtFileNo (tùy chọn):",
    "Learned so far": "Mã đã nhận dạng",
    "Clear calibration": "Xóa hiệu chỉnh",
    "Instructions": "Hướng dẫn",
    "Run offset scan & read test": "Quét offset và kiểm tra dữ liệu",
    "Scanning… (stay in a game, up to ~45s)": "Đang quét… (hãy ở trong game, tối đa 45 giây)",
    "Offsets found": "Đã tìm thấy offset",
    "Check output": "Hãy kiểm tra kết quả",
    "Cannot read game": "Không đọc được dữ liệu game",
    "Clear log": "Xóa nhật ký",
    "Export diagnostics": "Xuất chẩn đoán",
    "Log cleared.": "Đã xóa nhật ký.",
    "Looking for D2R…": "Đang tìm D2R…",
    "Game not found": "Không tìm thấy game",
    "Attach failed": "Không kết nối được",
    "Connected": "Đã kết nối",
    "Searching offsets…": "Đang tìm offset…",
    "Offsets unresolved": "Chưa nhận diện được offset",
    "Game closed": "Game đã đóng",
    "Health potion": "Bình máu",
    "Mana potion": "Bình mana",
    "Rejuvenation": "Bình hồi phục",
    "Merc health (Shift)": "Đệ uống máu (Shift)",
    "Merc rejuv (Shift)": "Đệ uống hồi phục (Shift)",
    "Healing potion at": "Uống máu khi",
    "Nothing learned yet — follow the steps below to teach the app how to identify potions.": "Chưa có mã bình nào. Hãy làm theo hướng dẫn bên dưới.",
    "Using built-in Infernal potion defaults.": "Đang sử dụng mã bình Infernal mặc định.",
    "Global hotkey cleared.": "Đã xóa phím bật/tắt.",
    "Enter a profile name first.": "Vui lòng nhập tên cấu hình.",
    "No profile selected to load.": "Chưa chọn cấu hình để nạp.",
    "Select a saved potion-code set first.": "Chọn bộ mã bình đã lưu trước.",
    "Connect to the game first, then scan.": "Kết nối game trước, sau đó mới quét.",
    "Scanning…": "Đang quét…",
    "Cannot enable: not connected / offsets unresolved. See Diagnostics.": "Không thể bật: chưa kết nối hoặc offset chưa hợp lệ. Xem Chẩn đoán.",
    "Press combo… (Esc clears)": "Nhấn tổ hợp phím… (Esc để xóa)",
    "hold Ctrl/Alt/Shift + a key": "Giữ Ctrl/Alt/Shift và nhấn một phím",
    "unsupported key": "Phím không hỗ trợ",
    "invalid combo": "Tổ hợp phím không hợp lệ",
    "active": "Đang hoạt động",
    "failed (in use?)": "Thất bại (phím đang được dùng?)",
    "Saved to": "Đã lưu vào",
    "Could not write diagnostics file.": "Không thể lưu file chẩn đoán.",
    "Unknown": "Không rõ",
}
PREFIX = (
    ("Hotkey: ", "Phím bật/tắt: "),
    ("Potions used: ", "Số bình đã uống: "),
    ("Belt: ", "Dây đai: "),
    ("Inventory: ", "Túi đồ: "),
    ("Scan failed: ", "Quét thất bại: "),
    ("Attach failed: ", "Kết nối thất bại: "),
    ("Unsupported key for column ", "Phím không hỗ trợ cho cột "),
    ("Saved to ", "Đã lưu vào "),
)
LONG = {
    "Attach to D2R and resolve offsets.": "Kết nối vào D2R và xác định offset. Dùng Kết nối lại nếu đã khởi động lại game.",
    "Turn auto-potion drinking on/off": "Bật hoặc tắt tính năng tự uống bình (cũng có thể dùng phím bật/tắt toàn cục).",
    "Set a global key combo": "Đặt tổ hợp phím bật/tắt AutoPotion khi đang chơi. Giữ Ctrl/Alt/Shift và nhấn phím; Esc để xóa.",
    "Presets set trigger thresholds": "Các mẫu chỉ thay đổi ngưỡng uống và thời gian chờ. Phím tắt, số bình và giới hạn thủ công được giữ nguyên.",
    "The app drinks when a bar drops": "AutoPotion sẽ uống bình khi máu hoặc mana giảm tới ngưỡng đã đặt. Di chuột lên từng mục để xem chi tiết.",
    "Drinks a health potion when": "Uống bình máu khi HP giảm xuống tỷ lệ đã đặt.",
    "Drinks a mana potion when": "Uống bình mana khi MP giảm xuống tỷ lệ đã đặt.",
    "Potions restore over time": "Bình máu và mana hồi dần theo thời gian. Biên an toàn giúp tránh uống bình quá sớm hoặc lãng phí.",
    "Emergency line: at/below this HP": "Ngưỡng HP khẩn cấp: ưu tiên dùng bình hồi phục tức thì thay cho bình máu.",
    "Emergency line for mana": "Ngưỡng MP khẩn cấp: ưu tiên bình hồi phục tức thì thay cho bình mana.",
    "Feeds the mercenary a health potion": "Cho lính đánh thuê uống bình máu khi HP xuống ngưỡng.",
    "Feeds the mercenary a rejuv": "Cho lính đánh thuê uống bình hồi phục khi HP nguy cấp.",
    "Tracks how fast you lose Life/Mana": "Dự đoán tốc độ mất máu và mana để uống sớm trước khi giảm xuống ngưỡng.",
    "When HP hits the rejuv line": "Khi máu xuống mức nguy hiểm, tính năng có thể sử dụng các bình phía trên để tiếp cận bình hồi phục. Có thể tốn thêm bình.",
    "Tick a column to let the app drink": "Đánh dấu cột dây đai muốn dùng. Chọn đúng phím đã gán trong game; Enter để lưu và Esc/Delete để trở về mặc định.",
    "When enabled, the app creates a real Xbox controller": "Khi bật, ứng dụng dùng API tay cầm Xbox có sẵn của Windows. Hãy kiểm tra tương thích trước khi sử dụng.",
    "To give a potion to your mercenary": "Để lính đánh thuê uống bình, ứng dụng giữ phím bổ trợ cùng phím dây đai (ví dụ Shift + Q). Đặt giống cấu hình trong game.",
    "Briefly brings the game window": "Đưa cửa sổ game lên trước trong chốc lát để D2R nhận phím ngay cả khi cửa sổ khác đang được chọn.",
    "A 'potion code set' is": "Bộ mã bình dùng để nhận dạng loại và cấp bình. Bộ mã này được lưu riêng với cấu hình tổng.",
    "Comma-separated (e.g. 271, 338)": "Nhập nhiều mã ngăn cách bằng dấu phẩy (ví dụ 271, 338). Chỉ cần khi không nhận diện được lính đánh thuê.",
    "Run this while in a game.": "Chỉ chạy khi đã vào game. Các chữ ký phải là RESOLVED và dữ liệu đọc phải hợp lệ. Nếu không, hãy gửi kết quả bên dưới để kiểm tra.",
    "Potions are identified by an internal code": (
        "Bình thuốc được nhận dạng bằng mã nội bộ. Mã có thể thay đổi theo phiên bản game.\n\n"
        "1. Vào game, đặt CÙNG một loại bình vào cả 4 góc dây đai (dây đai ít nhất 2 hàng).\n"
        "2. Chọn đúng loại bình đó trong danh sách rồi nhấn 'Quét bốn góc dây đai'.\n"
        "3. Ứng dụng tự đọc mã bình, lưu kết quả và nhận diện các bình cùng nhóm khi mã liên tiếp.\n"
        "4. Lặp lại với các loại bình khác đang dùng, sau đó bắt đầu chơi."
    ),
}
def tr(value):
    """Return only display text; never mutates application state."""
    if not isinstance(value, str):
        return value
    if value in LABELS:
        return LABELS[value]
    for prefix, translation in LONG.items():
        if value.startswith(prefix):
            return translation
    if value.startswith("uptime "):
        return value.replace("uptime ", "thời gian ", 1).replace(" potions", " bình").replace(" errors", " lỗi")
    if value.startswith("In game"):
        return value.replace("In game", "Đang trong game", 1).replace("menus open", "đang mở menu")
    if value.startswith("Belt: ") and "\nInventory: " in value:
        return value.replace("Belt: ", "Dây đai: ", 1).replace("\nInventory: ", "\nTúi đồ: ", 1)
    for a, b in PREFIX:
        if value.startswith(a):
            return b + value[len(a):]
    if value.startswith("Auto-potion enabled."): return "AutoPotion đã bật."
    if value.startswith("Auto-potion disabled."): return "AutoPotion đã tắt."
    return re.sub(r"\bLvl (?=\d)", "Lv ", value)
