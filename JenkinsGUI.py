import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import json
from JenkinsController import JenkinsController

CONFIG_FILE = "jenkins_config.json"


class JenkinsGUI:
    def __init__(self, master):
        self.master = master
        master.geometry("800x600")
        master.configure(bg="#2d2d2d")

        # 控制器初始化
        self.controller = JenkinsController()
        self.controller.set_log_callback(self.update_log_display)
        self.load_config()

        # 界面组件
        self.create_widgets()
        self.update_status()

    def create_widgets(self):
        # 路径配置区域
        path_frame = tk.Frame(self.master, bg="#3d3d3d", padx=10, pady=10)
        path_frame.grid(row=0, column=0, columnspan=3, sticky="ew")

        tk.Label(path_frame, text="Jenkins War路径:", fg="white", bg="#3d3d3d").grid(row=0, column=0)
        self.war_path_entry = tk.Entry(path_frame, width=50, bg="#4d4d4d", fg="white")
        self.war_path_entry.insert(0, self.controller.jenkins_war or "")
        self.war_path_entry.grid(row=0, column=1, padx=5)

        tk.Button(path_frame, text="浏览...", command=self.browse_war,
                  bg="#5d5d5d", fg="white").grid(row=0, column=2)

        # 操作按钮区域
        btn_frame = tk.Frame(self.master, bg="#3d3d3d", padx=10, pady=10)
        btn_frame.grid(row=1, column=0, columnspan=3, sticky="ew")

        button_style = {"bg": "#4d4d4d", "fg": "white", "padx": 10, "pady": 5}
        tk.Button(btn_frame, text="启动", command=self.start_jenkins, ** button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="停止", command=self.stop_jenkins, ** button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="重启", command=self.restart_jenkins, ** button_style).pack(side=tk.LEFT, padx=5)

        # 浏览器设置区域
        self.auto_open_var = tk.BooleanVar(value=True)
        tk.Checkbutton(path_frame, text="启动后自动打开浏览器", variable=self.auto_open_var,
                       bg="#3d3d3d", fg="white", selectcolor="#4d4d4d").grid(row=1, columnspan=3, pady=5)

        # URL配置
        tk.Label(path_frame, text="访问地址:", bg="#3d3d3d", fg="white").grid(row=2, column=0)
        self.url_entry = tk.Entry(path_frame, width=50, bg="#4d4d4d", fg="white")
        self.url_entry.insert(0, "http://localhost:5016")
        self.url_entry.grid(row=2, column=1, padx=5)

        # 状态显示
        self.status_label = tk.Label(self.master, text="状态: 检测中...", fg="#00ff00", bg="#2d2d2d")
        self.status_label.grid(row=2, column=0, columnspan=3, pady=10)

        # 日志显示区域
        self.log_area = ScrolledText(self.master, wrap=tk.WORD, state='disabled',
                                     bg="#1d1d1d", fg="white", insertbackground="white")
        self.log_area.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # 日志标签配置
        self.log_area.tag_config("INFO", foreground="#888888")
        self.log_area.tag_config("ERROR", foreground="#ff4444")
        self.log_area.tag_config("WARN", foreground="#ffaa00")

    def browse_war(self):
        path = filedialog.askopenfilename(title="选择jenkins.war", filetypes=[("WAR Files", "*.war")])
        if path:
            self.war_path_entry.delete(0, tk.END)
            self.war_path_entry.insert(0, path)
            self.controller.jenkins_war = path
            self.save_config()

    def update_status(self):
        status = "运行中" if self.controller.is_running() else "已停止"
        color = "#00ff00" if "运行" in status else "#ff0000"
        self.status_label.config(text=f"状态: {status}", fg=color)
        self.master.after(2000, self.update_status)

    def update_log_display(self, log_entry, level):
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, log_entry, level)
        self.log_area.see(tk.END)
        self.log_area.configure(state='disabled')

    def start_jenkins(self):
        try:
            # 获取界面配置
            self.controller.auto_open = self.auto_open_var.get()
            self.controller.jenkins_url = self.url_entry.get()
            if self.controller.start():
                messagebox.showinfo("成功", "Jenkins已启动")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def stop_jenkins(self):
        if self.controller.stop():
            messagebox.showinfo("成功", "Jenkins已停止")

    def restart_jenkins(self):
        if self.controller.restart():
            messagebox.showinfo("成功", "Jenkins已重启")

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({
                'war_path': self.controller.jenkins_war,
                'jenkins_home': self.controller.jenkins_home
            }, f)

    def load_config(self):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.controller.jenkins_war = config.get('war_path')
                self.controller.jenkins_home = config.get('jenkins_home')
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Jenkins服务管理器")
    app = JenkinsGUI(root)
    root.mainloop()