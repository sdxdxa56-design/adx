"""
keep_alive.py - إبقاء التطبيق نشطاً
"""

import requests
import time
import threading
from datetime import datetime

class KeepAlive:
    """فئة لإبقاء التطبيق نشطاً"""
    
    def __init__(self, app_url: str, interval: int = 300):
        self.app_url = app_url
        self.interval = interval  # ثانية بين كل طلب
        self.is_running = False
        self.thread = None
    
    def start(self):
        """بدء خدمة إبقاء التطبيق نشطاً"""
        self.is_running = True
        self.thread = threading.Thread(target=self._keep_alive_loop, daemon=True)
        self.thread.start()
        print(f"✅ بدأت خدمة Keep-Alive للتطبيق: {self.app_url}")
    
    def stop(self):
        """إيقاف الخدمة"""
        self.is_running = False
        if self.thread:
            self.thread.join()
        print("⏹️ توقفت خدمة Keep-Alive")
    
    def _keep_alive_loop(self):
        """حلقة إبقاء التطبيق نشطاً"""
        while self.is_running:
            try:
                response = requests.get(self.app_url, timeout=10)
                print(f"🟢 Keep-Alive ping: {response.status_code} - {datetime.now()}")
            except Exception as e:
                print(f"🔴 Keep-Alive error: {e}")
            
            time.sleep(self.interval)
    
    def ping_once(self):
        """طلب واحد لإبقاء التطبيق نشطاً"""
        try:
            response = requests.get(self.app_url, timeout=10)
            return {
                "status": "success",
                "status_code": response.status_code,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

# استخدام الملف
if __name__ == "__main__":
    # استبدل هذا بالرابط الفعلي للتطبيق
    app_url = "https://your-app.streamlit.app/"
    
    keeper = KeepAlive(app_url, interval=600)  # كل 10 دقائق
    keeper.start()
    
    # إبقاء السكريبت يعمل
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        keeper.stop()