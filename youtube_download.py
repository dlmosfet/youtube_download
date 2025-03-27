import tkinter as tk
from tkinter import filedialog
import yt_dlp as ytdlp
import tkinter.messagebox as messagebox
import threading
import socket
import os


class YouTubeDownloader:
    def __init__(self, master):
        self.master = master
        master.title("YouTube Downloader")
        master.geometry("500x350")

        # 預設下載目錄
        self.default_download_dir = os.path.expanduser("~/Downloads")

        # 建立元件
        self.create_widgets()

    def create_widgets(self):
        # 標題
        tk.Label(self.master, text="輸入YouTube影片網址").pack(pady=10)

        # 網址輸入框
        self.url_entry = tk.Entry(self.master, width=50)
        self.url_entry.pack()
        self.url_entry.bind("<KeyRelease>", lambda event: self.update_quality_options())

        # 畫質下拉選單
        tk.Label(self.master, text="選擇影片畫質").pack(pady=10)
        self.quality_var = tk.StringVar(value="自動（最高畫質）")
        self.quality_menu = tk.OptionMenu(self.master, self.quality_var, "自動（最高畫質）")
        self.quality_menu.pack()

        # 檔案儲存位置
        tk.Label(self.master, text="選擇下載檔案儲存位置").pack(pady=10)
        self.download_dir = tk.StringVar(value=self.default_download_dir)
        tk.Label(self.master, textvariable=self.download_dir).pack()
        tk.Button(self.master, text="選擇位置", command=self.choose_directory).pack()

        # 下載按鈕
        tk.Button(self.master, text="下載", command=self.start_download_thread).pack(pady=10)

        # 狀態列
        self.status_label = tk.Label(self.master, text="")
        self.status_label.pack(pady=10)

    def choose_directory(self):
        download_dir = filedialog.askdirectory()
        if download_dir:
            self.download_dir.set(download_dir)

    def on_progress_callback(self, d):
        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes', 1)
            percent = (downloaded / total) * 100
            msg = f"已下載 {downloaded / (1024 * 1024):.2f} MB / {total / (1024 * 1024):.2f} MB ({percent:.2f}%)"
            self.status_label.config(text=msg)
            self.master.update()

    def is_connected(self):
        """檢查是否有網路連線"""
        try:
            socket.create_connection(("www.google.com", 80), timeout=5)
            return True
        except OSError:
            return False

    def update_quality_options(self, *args):
        url = self.url_entry.get()
        if not url:
            return
        if not self.is_connected():
            messagebox.showerror("錯誤", "無法更新畫質選項，請檢查網路連線")
            return

        try:
            ydl_opts = {'quiet': True}
            with ytdlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                formats = info_dict.get('formats', [])
                quality_options = []

                for f in formats:
                    if f.get('format_note') and f.get('ext') == 'mp4':
                        quality_options.append(f['format_note'])

                quality_options = list(set(quality_options))
                quality_options.sort()

                # 更新畫質選單
                self.quality_menu['menu'].delete(0, 'end')
                for option in ["自動（最高畫質）"] + quality_options:
                    self.quality_menu['menu'].add_command(label=option, command=tk._setit(self.quality_var, option))

        except Exception as e:
            messagebox.showerror("錯誤", f"無法更新畫質選項: {str(e)}")

    def download_video(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("錯誤", "請輸入影片網址")
            return
        if not self.is_connected():
            messagebox.showerror("錯誤", "無法下載影片，請檢查網路連線")
            return

        download_path = self.download_dir.get()
        if not os.path.exists(download_path):
            messagebox.showerror("錯誤", "選擇的下載位置無效，請重新選擇")
            return

        selected_quality = self.quality_var.get()

        # 解析畫質選項
        if selected_quality == "自動（最高畫質）":
            format_option = "bestvideo+bestaudio/best"
        else:
            format_option = f"bestvideo[format_note={selected_quality}]+bestaudio/best"

        try:
            ydl_opts = {
                'outtmpl': os.path.join(download_path, "%(title)s.%(ext)s"),
                'progress_hooks': [self.on_progress_callback],
                'format': format_option,
            }

            with ytdlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.status_label.config(text="下載完成！")

        except Exception as e:
            messagebox.showerror("錯誤", f"下載過程中出現錯誤: {str(e)}")

    def start_download_thread(self):
        """使用執行緒下載，防止 GUI 凍結"""
        threading.Thread(target=self.download_video, daemon=True).start()


root = tk.Tk()
yt_downloader = YouTubeDownloader(root)
root.mainloop()
