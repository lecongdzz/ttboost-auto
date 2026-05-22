import threading
import time
import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.lang import Builder

# Thư viện quản lý kết nối ADB trực tiếp bằng Socket không qua file adb.exe/adb binary
from adb_shell.adb_device import AdbDeviceTcp

# --- 🎨 BỘ MÃ MÀU MARKUP KIVY (CHUYỂN TỪ ANSI ĐỂ HIỂN THỊ TRÊN GIAO DIỆN) ---
C_CYAN = "[color=00ffff]"
C_GREEN = "[color=22ff22]"
C_YELLOW = "[color=ffff00]"
C_RED = "[color=ff3333]"
C_RESET = "[/color]"

# --- 🛡️ HÀM TỰ SÁT NẾU BỊ ĐỔI CHỮ KÝ (ANTI-CRACK CHUẨN ANDROID) ---
def check_apk_signature():
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        context = PythonActivity.mActivity
        package_manager = context.getPackageManager()
        package_name = context.getPackageName()
        
        package_info = package_manager.getPackageInfo(package_name, package_manager.GET_SIGNATURES)
        app_signature = package_info.signatures[0].hashCode()
        
        # Số hash gốc của bạn (Thay số này bằng số mã hash Keystore thực tế của bạn)
        ORIGINAL_SIGNATURE_HASH = 123456789 
        
        if app_signature != ORIGINAL_SIGNATURE_HASH:
            import sys
            sys.exit() # Khác chữ ký phát hiện mod -> Sập app khẩn cấp
    except:
        pass # Chạy trên PC hoặc Pydroid 3 chưa đóng gói sẽ tự động bỏ qua, không gây lỗi code

# --- 📺 GIAO DIỆN APP (KV LANGUAGE) ---
KV_INTERFACE = """
MainInterface:
    orientation: 'vertical'
    padding: [15, 10, 15, 10]
    spacing: 10
    canvas.before:
        Color:
            rgba: 0.02, 0.05, 0.08, 1
        Rectangle:
            pos: self.pos
            size: self.size

    Label:
        text: "TTBoost Automation VIP - Adm Lê Công"
        size_hint_y: None
        height: 30
        bold: True
        color: 0, 1, 0.8, 1

    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: 60
        padding: 5
        canvas.before:
            Color:
                rgba: 0, 0.8, 0.8, 1
            Line:
                rounded_rectangle: (self.x, self.y, self.width, self.height, 8)
                width: 1.2
        Label:
            text: "🌐 Website: tangtuongtacsieure.com"
            color: 0, 0.9, 0.9, 1
            font_size: '14sp'
        Label:
            text: "💻 Powered by Viettask Software"
            color: 0.8, 0.8, 0.8, 1
            font_size: '11sp'

    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: 100
        spacing: 2
        Label:
            text: "👑 [color=1e90ff]CEO FOUNDER VIETTASK GROUP[/color]"
            markup: True
            text_size: self.size
            halign: 'left'
        Label:
            text: "👤 [b]LƯƠNG HUỲNH ĐỨC (NHÀ SÁNG LẬP)[/b]"
            markup: True
            text_size: self.size
            halign: 'left'
        Label:
            text: "📞 [color=ffaa00]SĐT: 0886317315[/color]"
            markup: True
            text_size: self.size
            halign: 'left'
        Label:
            text: "⚙️ [color=22ff22]LƯƠNG TRƯỜNG PHƯỚC (VẬN HÀNH SERVER)[/color]"
            markup: True
            text_size: self.size
            halign: 'left'
        Label:
            text: "🧑‍💻 [color=ff00ff]LẬP TRÌNH VIÊN: LÊ CÔNG[/color]"
            markup: True
            text_size: self.size
            halign: 'left'

    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: 60
        spacing: 3
        Label:
            text: "▶ Cấu hình Địa chỉ IP ADB (IP:PORT):"
            color: 0.2, 0.8, 0.2, 1
            text_size: self.size
            halign: 'left'
        TextInput:
            id: adb_input
            text: "127.0.0.1:5555"
            multiline: False
            background_color: 0.15, 0.15, 0.15, 1
            foreground_color: 1, 1, 1, 1
            font_size: '15sp'
            padding_y: [8, 8]

    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: 60
        spacing: 3
        Label:
            text: "▶ Nhập số xu mục tiêu cần cày để dừng:"
            color: 0.2, 0.8, 0.8, 1
            text_size: self.size
            halign: 'left'
        TextInput:
            id: target_input
            text: "1000"
            multiline: False
            background_color: 0.15, 0.15, 0.15, 1
            foreground_color: 1, 1, 1, 1
            font_size: '15sp'
            padding_y: [8, 8]

    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: 40
        spacing: 8
        Button:
            text: "Chi Follow"
            background_color: 0, 0.4, 0.4, 1
            on_press: root.start_automation_thread('1')
        Button:
            text: "Chi Tym"
            background_color: 0, 0.3, 0.5, 1
            on_press: root.start_automation_thread('2')
        Button:
            text: "Tổng Lực"
            background_color: 0, 0.6, 0.2, 1
            bold: True
            on_press: root.start_automation_thread('3')

    BoxLayout:
        orientation: 'vertical'
        spacing: 5
        Label:
            text: "Log Trạng Thái:"
            text_size: self.size
            halign: 'left'
            size_hint_y: None
            height: 18
            bold: True
        ScrollView:
            id: scroller
            canvas.before:
                Color:
                    rgba: 0.05, 0.08, 0.12, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                text: root.log_text
                markup: True
                size_hint_y: None
                height: self.texture_size[1]
                text_size: self.width, None
                padding: [10, 10]
                valign: 'top'

    Button:
        text: "🛑 DỪNG TOOL AN TOÀN (EMERGENCY)"
        size_hint_y: None
        height: 42
        background_color: 0.8, 0.2, 0.1, 1
        bold: True
        on_press: root.stop_automation()
"""

# --- 🧠 XỬ LÝ LOGIC HOẠT ĐỘNG ---
class MainInterface(BoxLayout):
    log_text = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_running = False
        self.device = None
        self.CACHED_FOLLOW_X = None
        self.CACHED_FOLLOW_Y = None
        self.pkg = "com.ttboost.app" 
        self.append_log(f"{C_CYAN}[+] Hệ thống sẵn sàng. Nhập thông số và chọn chế độ để khởi chạy!{C_RESET}")

    def append_log(self, text):
        self.log_text += f"{text}\n"
        Clock.schedule_once(lambda dt: setattr(self.ids.scroller, 'scroll_y', 0))

    def log_from_thread(self, text):
        Clock.schedule_once(lambda dt: self.append_log(text))

    def start_automation_thread(self, job_type):
        if self.is_running:
            self.log_from_thread(f"{C_RED}[!] Tool đang chạy rồi, vui lòng bấm Dừng trước!{C_RESET}")
            return
        
        self.is_running = True
        threading.Thread(target=self.run_logic, args=(job_type,), daemon=True).start()

    def stop_automation(self):
        if self.is_running:
            self.is_running = False
            self.log_from_thread(f"{C_RED}[🛑] ĐÃ PHÁT LỆNH DỪNG TOOL KHẨN CẤP!{C_RESET}")
        else:
            self.log_from_thread("[*] Hệ thống hiện tại không chạy.")

    def parse_element_coords(self, xml_data, keywords):
        for keyword in keywords:
            pattern = r'(text|content-desc)="[^"]*' + re.escape(keyword) + r'[^"]*".*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
            match = re.search(pattern, xml_data, re.IGNORECASE)
            if match:
                x = (int(match.group(2)) + int(match.group(4))) // 2
                y = (int(match.group(3)) + int(match.group(5))) // 2
                return x, y
        return None

    def run_logic(self, job_type):
        raw_ip = self.ids.adb_input.text.strip()
        target_coins = int(self.ids.target_input.text.strip())
        
        try:
            ip, port = raw_ip.split(":")
            port = int(port)
        except:
            self.log_from_thread(f"{C_RED}[!] Định dạng IP:PORT không hợp lệ! (Ví dụ đúng: 127.0.0.1:5555){C_RESET}")
            self.is_running = False
            return

        self.log_from_thread(f"{C_CYAN}[⚡] Đang kết nối Socket tới {ip}:{port}...{C_RESET}")
        
        try:
            self.device = AdbDeviceTcp(ip, port, default_transport_timeout_s=5)
            self.device.connect(auth_timeout_s=5)
            self.log_from_thread(f"{C_GREEN}[✓] Kết nối ADB Local thành công! Ép xung V3.3 Ultimate...{C_RESET}")
        except Exception as e:
            self.log_from_thread(f"{C_RED}[X] Lỗi kết nối! Hãy chắc chắn đã bật Wireless Debugging. {str(e)}{C_RESET}")
            self.is_running = False
            return

        count = 0
        earned_slots = 0 
        
        while self.is_running:
            try:
                count += 1
                if earned_slots >= target_coins:
                    self.log_from_thread(f"{C_GREEN}[✓] Đã đạt mục tiêu {target_coins} xu! Tự động dừng hệ thống.{C_RESET}")
                    break

                self.log_from_thread(f"[*] Vòng {count}: Đang quét cấu trúc TTBoost...")
                current_job = ""

                while self.is_running:
                    self.device.shell("uiautomator dump /sdcard/v.xml")
                    xml_data = self.device.shell("cat /sdcard/v.xml")

                    if not xml_data:
                        time.sleep(0.5)
                        continue

                    if "completed the task" in xml_data or "Error" in xml_data:
                        coords = self.parse_element_coords(xml_data, ["Skip", "Bỏ qua"])
                        if coords: self.device.shell(f"input tap {coords[0]} {coords[1]}")
                        self.log_from_thread(f"{C_RED}[▲] Phát hiện lỗi, Skip!{C_RESET}")
                        time.sleep(1.0)
                        continue

                    if "OK" in xml_data or "Đóng" in xml_data or "Close" in xml_data:
                        coords = self.parse_element_coords(xml_data, ["OK", "Đóng", "Close"])
                        if coords: self.device.shell(f"input tap {coords[0]} {coords[1]}")
                        time.sleep(0.5)
                        continue

                    follow_coords = self.parse_element_coords(xml_data, ["Follow +", "Theo dõi +"])
                    like_coords = self.parse_element_coords(xml_data, ["Like +", "Thích +"])
                    skip_coords = self.parse_element_coords(xml_data, ["Skip", "Bỏ qua"])

                    job_found = False

                    if job_type == '1': 
                        if follow_coords:
                            self.device.shell(f"input tap {follow_coords[0]} {follow_coords[1]}")
                            current_job = "follow"
                            job_found = True
                        elif like_coords and skip_coords:
                            self.device.shell(f"input tap {skip_coords[0]} {skip_coords[1]}")
                            self.log_from_thread(f"{C_YELLOW}-> [Lọc Job] Gặp Tym -> Ép bỏ qua!{C_RESET}")
                            time.sleep(1.5)
                            continue

                    elif job_type == '2': 
                        if like_coords:
                            self.device.shell(f"input tap {like_coords[0]} {like_coords[1]}")
                            current_job = "like"
                            job_found = True
                        elif follow_coords and skip_coords:
                            self.device.shell(f"input tap {skip_coords[0]} {skip_coords[1]}")
                            self.log_from_thread(f"{C_YELLOW}-> [Lọc Job] Gặp Follow -> Ép bỏ qua!{C_RESET}")
                            time.sleep(1.5)
                            continue

                    elif job_type == '3': 
                        if follow_coords:
                            self.device.shell(f"input tap {follow_coords[0]} {follow_coords[1]}")
                            current_job = "follow"
                            job_found = True
                        elif like_coords:
                            self.device.shell(f"input tap {like_coords[0]} {like_coords[1]}")
                            current_job = "like"
                            job_found = True

                    if job_found:
                        break
                    else:
                        time.sleep(0.5)

                if not self.is_running: break

                self.log_from_thread(f"{C_GREEN}-> Nhận dạng [{current_job.upper()}]. Mở TikTok...{C_RESET}")
                time.sleep(2.5) 

                if current_job == "like":
                    tiktok_xml = self.device.shell("uiautomator dump /sdcard/v.xml && cat /sdcard/v.xml")
                    coords = self.parse_element_coords(tiktok_xml, ["Like", "Thích", "Button, Like"])
                    if coords:
                        self.device.shell(f"input tap {coords[0]} {coords[1]}")
                    else:
                        self.device.shell("input tap 540 960")
                        time.sleep(0.08)
                        self.device.shell("input tap 540 960")
                    time.sleep(1.0)
                    earned_slots += 1 

                elif current_job == "follow":
                    if self.CACHED_FOLLOW_X and self.CACHED_FOLLOW_Y:
                        self.device.shell(f"input tap {self.CACHED_FOLLOW_X} {self.CACHED_FOLLOW_Y}")
                    else:
                        tiktok_xml = self.device.shell("uiautomator dump /sdcard/v.xml && cat /sdcard/v.xml")
                        coords = self.parse_element_coords(tiktok_xml, ["Follow", "Theo dõi", "Follow button"])
                        if coords:
                            self.CACHED_FOLLOW_X, self.CACHED_FOLLOW_Y = coords[0], coords[1]
                            self.device.shell(f"input tap {coords[0]} {coords[1]}")
                        else:
                            self.device.shell("input tap 900 800")
                    time.sleep(1.0)
                    earned_slots += 1

                if not self.is_running: break

                self.device.shell(f"monkey -p {self.pkg} -c android.intent.category.LAUNCHER 1")
                time.sleep(0.8) 
                self.log_from_thread(f"{C_GREEN}[b][✓] Earned: {earned_slots} / Target: {target_coins}[/b]{C_RESET}")

            except Exception as loop_error:
                self.log_from_thread(f"{C_RED}[!] Lỗi vòng lặp: {str(loop_error)}{C_RESET}")
                time.sleep(1)

        self.is_running = False

# --- 🚀 KHỞI CHẠY APP ---
class TTBoostApp(App):
    def build(self):
        return Builder.load_string(KV_INTERFACE)

if __name__ == '__main__':
    # Chạy hàm kiểm tra chữ ký trước khi khởi dựng UI
    check_apk_signature()
    TTBoostApp().run()
