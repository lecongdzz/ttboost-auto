import os
import time
import hashlib
import flet as ft 

# --- HÀM BẢO MẬT: TẠO VÀ KIỂM TRA KEY THEO THIẾT BỊ ---
def get_device_id():
    """Lấy mã định danh duy nhất của thiết bị để khóa Key"""
    try:
        # Thử lấy số seri hoặc model máy để định danh chống crack
        device_info = os.popen("getprop ro.serialno").read().strip()
        if not device_info:
            device_info = os.popen("getprop ro.product.model").read().strip()
        if not device_info:
            device_info = "VIETTASK_USER_MOBILE"
        return hashlib.md5(device_info.encode()).hexdigest()[:12].upper()
    except:
        return "DEV123456789"

def generate_valid_key(device_id):
    """Thuật toán tạo Key riêng biệt của bạn (Dùng để cấp cho khách)"""
    secret_salt = "VIP_LE_CONG_2026"
    raw_str = device_id + secret_salt
    return hashlib.sha256(raw_str.encode()).hexdigest()[:16].upper()

def main_app(page: ft.Page):
    page.title = "TTBoost Automation VIP"
    page.background_color = "#000000"
    page.padding = 15
    page.scroll = "auto"

    DEVICE_ID = get_device_id()
    VALID_KEY = generate_valid_key(DEVICE_ID)

    # --- KHAI BÁO BIẾN TRẠNG THÁI ---
    earned_coins = 240
    target_coins = 1000

    # --- CÁC THÀNH PHẦN GIAO DIỆN ---
    # Header hiển thị thông tin phần mềm
    header = ft.Container(
        content=ft.Column([
            ft.Text("TTBoost Automation VIP - Adm Lê Công", color="#00FFFF", size=16, weight="bold"),
            ft.Text("🌐 Website: tangtuongtacsieure.com", color="#00FF00", size=13),
            ft.Text("💻 Powered by Viettask Software", color="#888888", size=11),
        ], horizontal_alignment="center"),
        border=ft.border.all(1.5, "#00FFFF"),
        border_radius=8,
        padding=10,
        alignment=ft.alignment.center
    )

    # Thông tin ban quản trị tác giả
    author_info = ft.Column([
        ft.Text("👑 CEO FOUNDER VIETTASK GROUP", color="#FF00FF", size=12, weight="bold"),
        ft.Text("👤 LƯƠNG HUỲNH ĐỨC (NHÀ SÁNG LẬP)", color="#00BFFF", size=12),
        ft.Text("📞 SĐT: 0886317315", color="#FFA500", size=12),
        ft.Text("⚙️ LƯƠNG TRƯỜNG PHƯỚC (VẬN HÀNH SERVER)", color="#00FF00", size=12),
        ft.Text("👨‍💻 LẬP TRÌNH VIÊN: LÊ CÔNG", color="#BA55D3", size=12),
    ], spacing=3)

    # Các ô nhập thông số cấu hình
    ip_input = ft.TextField(label="▶ Cấu hình Địa chỉ IP ADB (IP:PORT):", value="127.0.0.1:5555", border_color="#00FFFF", text_size=13)
    target_input = ft.TextField(label="▶ Nhập số xu mục tiêu cần chạy để dừng:", value="1000", border_color="#00FFFF", text_size=13)

    # Nhật ký hệ thống Log Trạng Thái giống 100% demo thực tế
    log_title = ft.Text("Log Trạng Thái:", color="#FFFFFF", weight="bold", size=13)
    auth_log = ft.Text("[+] Trạng thái bản quyền: Đang chờ xác thực...", color="#FFA500", size=12)
    status_log = ft.Text("[*] Đang chờ kích hoạt hệ thống...", color="#FFFFFF", size=12)
    error_log = ft.Text("[⚠️] Hệ thống an toàn bảo mật đang bật", color="#00FFFF", size=12)
    stats_log = ft.Text(f"📊 [b]Earned: {earned_coins} / Target: {target_coins}[/b]", color="#FF00FF", weight="bold", size=14)

    log_box = ft.Container(
        content=ft.Column([
            log_title,
            ft.Divider(color="#333333"),
            auth_log,
            status_log,
            error_log,
            ft.Container(height=5),
            stats_log
        ], spacing=3),
        bgcolor="#0A1118",
        border_radius=8,
        padding=10,
        border=ft.border.all(1, "#222222"),
    )

    # Màn hình khóa bản quyền anti-crack chuyên nghiệp
    key_input = ft.TextField(label=f"Nhập KEY kích hoạt (Mã máy của bạn: {DEVICE_ID})", border_color="#FF0000", password=True, can_reveal_password=True)
    
    def check_key_click(e):
        if key_input.value == VALID_KEY:
            auth_log.value = "[+] KÍCH HOẠT BẢN QUYỀN THÀNH CÔNG!"
            auth_log.color = "#00FF00"
            status_log.value = "[*] Trạng thái: Thiết bị đã sẵn sàng."
            status_log.color = "#00FFFF"
            auth_container.visible = False
            tool_controls.visible = True
            page.update()
        else:
            auth_log.value = "[⚠️] SAI KEY KÍCH HOẠT! VUI LÒNG LIÊN HỆ BAN QUẢN TRỊ."
            auth_log.color = "#FF0000"
            page.update()

    btn_check_key = ft.ElevatedButton("XÁC THỰC BẢN QUYỀN", on_click=check_key_click, bgcolor="#00FF00", color="#000000", width=250)

    auth_container = ft.Column([
        ft.Text("🛡️ HỆ THỐNG BẢO MẬT CHỐNG CRACK / BYPASS", color="#FF0000", weight="bold", size=13),
        key_input,
        ft.Row([btn_check_key], alignment="center")
    ], spacing=10)

    # Bộ điều khiển chế độ chạy ẩn lúc đầu, nhập đúng key mới mở khóa
    def start_tool(e):
        status_log.value = f"[*] Đang ép xung vận hành chế độ: {e.control.text}..."
        status_log.color = "#00FF00"
        page.update()
        # Nơi đây tích hợp gọi kịch bản xử lý adb từ file de.py cũ của bạn

    tool_controls = ft.Column([
        ft.Row([
            ft.ElevatedButton("Chi Follow", bgcolor="#00FFFF", color="#000000", on_click=start_tool),
            ft.ElevatedButton("Chi Tym", bgcolor="#1E90FF", color="#FFFFFF", on_click=start_tool),
            ft.ElevatedButton("Tổng Lực", bgcolor="#00FF00", color="#000000", on_click=start_tool),
        ], alignment="space_evenly"),
        ft.Container(height=5),
        ft.ElevatedButton("🛑 DỪNG TOOL AN TOÀN (EMERGENCY)", bgcolor="#8B0000", color="#FFFFFF", width=400, height=45)
    ], visible=False)

    # Sắp xếp bố cục nạp vào ứng dụng chính
    page.add(
        header,
        ft.Container(height=5),
        author_info,
        ft.Container(height=5),
        ip_input,
        ft.Container(height=5),
        target_input,
        ft.Container(height=10),
        auth_container,
        tool_controls,
        ft.Container(height=10),
        log_box
    )

# SỬA LỖI TẠI ĐÂY: Thêm tham số view để ép Flet mở giao diện không lỗi assets hệ thống trên mobile
if __name__ == "__main__":
    ft.app(target=main_app, view=ft.AppView.WEB_BROWSER)
