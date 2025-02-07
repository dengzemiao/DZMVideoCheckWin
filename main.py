import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取图标路径
icon_path = os.path.join(current_dir, "icon.ico")
# FFmpeg路径
FFMPEG_PATH = os.path.join(current_dir, 'ffmpeg', 'bin', 'ffmpeg.exe')

class VideoCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("【短剧组】视频文件检测工具")
        self.root.iconbitmap(icon_path)
        self.root.geometry("500x350")  # 增加一些空间以适应新的组件

        # 变量
        self.folder_path = tk.StringVar()  # 文件夹路径
        self.timeout = tk.IntVar(value=5)  # 默认超时时间
        self.running = False  # 是否正在检测
        self.progress = 0  # 检测进度
        self.total_files = 0  # 总文件数
        self.unplayable_videos = []  # 不可播放的视频文件

        # UI组件
        self.create_widgets()

    def create_widgets(self):
        """创建界面组件"""
        # 选择文件夹
        tk.Label(self.root, text="选择文件夹:").grid(row=0, column=0, padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.folder_path, width=40).grid(row=0, column=1, padx=10, pady=10)
        tk.Button(self.root, text="浏览", command=self.select_folder).grid(row=0, column=2, padx=10, pady=10)

        # 超时时间设置
        tk.Label(self.root, text="请输入超时时间(秒):").grid(row=1, column=0, padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.timeout, width=40).grid(row=1, column=1, padx=10, pady=10)

        # 超时提示
        tk.Label(self.root, text="建议超时时间: ").grid(row=2, column=0, padx=10, pady=10)
        tk.Label(self.root, text="3-10秒;几十MB>=3;几百MB>=5;几GB>=10;", width=40).grid(row=2, column=1, padx=10, pady=10)

        # 进度条
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        # 开始/停止按钮
        self.start_button = tk.Button(self.root, text="开始校验", command=self.start_check)
        self.start_button.grid(row=4, column=0, padx=10, pady=10)

        # 结果显示
        self.result_text = tk.Text(self.root, height=10, width=50)
        self.result_text.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

    def select_folder(self):
        """选择文件夹"""
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    def start_check(self):
        """开始检测"""
        if not self.folder_path.get():
            messagebox.showwarning("警告", "请先选择文件夹！")
            return

        # 获取用户输入的超时时间
        timeout_value = self.timeout.get()

        if timeout_value < 1 or timeout_value > 60:
            messagebox.showwarning("警告", "超时时间应在1到60秒之间！")
            return

        # 初始化
        self.running = True
        self.progress = 0
        self.unplayable_videos = []
        self.result_text.delete(1.0, tk.END)  # 清空结果显示
        self.start_button.config(state=tk.DISABLED)

        # 获取视频文件
        video_files = [
            f for f in os.listdir(self.folder_path.get())
            if f.endswith(('.mp4', '.avi', '.mkv', '.mov', '.flv'))
        ]
        self.total_files = len(video_files)

        if not video_files:
            messagebox.showinfo("提示", "文件夹中没有视频文件！")
            self.stop_check()
            return

        # 启动检测线程
        self.detection_thread = threading.Thread(target=self.check_videos, args=(video_files, timeout_value))
        self.detection_thread.start()

        self.result_text.insert(tk.END, "以下视频文件不可播放：\n")

        # 更新进度条
        self.update_progress()

    def stop_check(self):
        """停止检测"""
        self.running = False
        self.start_button.config(state=tk.NORMAL)

    def check_videos(self, video_files, timeout_value):
        """检测视频文件"""
        for idx, video_file in enumerate(video_files):
            if not self.running:
                break

            video_path = os.path.join(self.folder_path.get(), video_file)
            # 使用更快速的检测命令（仅检测关键帧）
            command = [FFMPEG_PATH, '-v', 'error', '-i', video_path, '-vf', 'select=eq(n\,0)', '-f', 'null', '-']

            try:
                subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                               creationflags=subprocess.CREATE_NO_WINDOW, timeout=timeout_value)  # 使用用户设置的超时时间
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                self.unplayable_videos.append(video_file)
                self.result_text.insert(tk.END, f"{video_file}\n")

            # 更新进度
            self.progress = (idx + 1) / self.total_files * 100

        # 检测完成
        self.running = False
        self.show_results()

    def update_progress(self):
        """更新进度条"""
        if self.running:
            self.progress_bar["value"] = self.progress
            self.root.after(50, self.update_progress)  # 每50ms更新一次
        else:
            self.progress_bar["value"] = 100

    def show_results(self):
        """显示检测结果"""
        if not self.unplayable_videos:
            self.result_text.insert(tk.END, "所有视频文件均可播放。\n")

        self.start_button.config(state=tk.NORMAL)

# 运行程序
if __name__ == "__main__":
    root = tk.Tk()
    app = VideoCheckerApp(root)
    root.mainloop()
