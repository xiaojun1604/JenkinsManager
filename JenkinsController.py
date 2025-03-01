import subprocess
import psutil
import os
import json
from pathlib import Path
from datetime import datetime
import traceback
import webbrowser
import socket
import time


class JenkinsController:
    def __init__(self, jenkins_war_path=None):
        self.jenkins_war = jenkins_war_path
        self.process = None
        self.jenkins_home = os.getenv("JENKINS_HOME", str(Path.home() / "jenkins_home"))
        self.log_file = "logs/operation.log"
        self._init_log_dir()
        self.log_callback = None

    def _init_log_dir(self):
        os.makedirs("logs", exist_ok=True)

    def _log(self, message, level="INFO"):
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {level}: {message}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        if self.log_callback:
            self.log_callback(log_entry, level)

    def set_log_callback(self, callback):
        self.log_callback = callback

    def set_jenkins_home(self, path):
        self.jenkins_home = path
        self._log(f"设置Jenkins主目录: {path}")

    def is_running(self):
        for proc in psutil.process_iter(['cmdline']):
            if proc.info['cmdline'] and 'jenkins.war' in ' '.join(proc.info['cmdline']):
                return True
        return False

    def start(self):
        try:
            if not self.jenkins_war or not Path(self.jenkins_war).exists():
                raise FileNotFoundError("Jenkins war文件路径无效")

            cmd = [
                'java', '-jar', self.jenkins_war,
                f'--webroot={self.jenkins_home}/war',
                f'--pluginroot={self.jenkins_home}/plugins',
                '--httpPort=5016'
            ]
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            self._log(f"启动成功 | PID: {self.process.pid}")

            # 新增：等待服务就绪后打开浏览器
            if self._wait_for_service(port=5016, timeout=30):
                self.open_browser()
            else:
                self._log("服务未在指定时间内就绪", "WARN")

            return True
        except Exception as e:
            error_msg = traceback.format_exc()
            self._log(f"启动失败: {str(e)}\n{error_msg}", "ERROR")
            raise

    def _wait_for_service(self, port=8080, timeout=30):
        """等待Jenkins服务就绪"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    s.connect(('localhost', port))
                return True
            except:
                time.sleep(1)
        return False

    def open_browser(self, url="http://localhost:5016"):
        """打开浏览器"""
        try:
            webbrowser.open_new_tab(url)
            self._log(f"已打开浏览器访问: {url}")
        except Exception as e:
            self._log(f"浏览器打开失败: {str(e)}", "ERROR")

    def stop(self):
        for proc in psutil.process_iter(['cmdline']):
            if proc.info['cmdline'] and 'jenkins.war' in ' '.join(proc.info['cmdline']):
                proc.terminate()
                proc.wait()
                self._log("服务已停止")
                return True
        self._log("停止失败: 未找到运行中的Jenkins", "WARN")
        return False

    def restart(self):
        self._log("尝试重启服务")
        if self.stop():
            return self.start()
        return False