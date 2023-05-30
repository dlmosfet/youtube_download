import tkinter as tk
from tkinter import filedialog
from pytube import YouTube
import tkinter.messagebox as messagebox


class YouTubeDownloader:
    def __init__(self, master):
        self.master = master
        master.title("YouTube Downloader")
        master.geometry("500x300")

        # 建立元件
        self.create_widgets()

        # 更新畫質選項
        self.update_quality_options()

    def create_widgets(self):
        # 標題
        tk.Label(self.master, text="輸入YouTube影片網址").pack(pady=10)

        # 網址輸入框
        self.url_entry = tk.Entry(self.master, width=50)
        self.url_entry.pack()

        # 畫質下拉選單
        tk.Label(self.master, text="選擇影片畫質").pack(pady=10)
        self.quality_var = tk.StringVar(value="自動（最高畫質）")
        self.quality_menu = tk.OptionMenu(self.master, self.quality_var, "自動（最高畫質）")
        self.quality_menu.pack()

        # 檔案儲存位置
        tk.Label(self.master, text="選擇下載檔案儲存位置").pack(pady=10)
        self.download_dir = tk.StringVar(value="選擇下載位置")
        tk.Label(self.master, textvariable=self.download_dir).pack()
        tk.Button(self.master, text="選擇位置", command=self.choose_directory).pack()

        # 下載按鈕
        tk.Button(self.master, text="下載", command=self.download_video).pack(pady=10)

        # 狀態列
        self.status_label = tk.Label(self.master, text="")
        self.status_label.pack(pady=10)

    def choose_directory(self):
        download_dir = filedialog.askdirectory()
        if download_dir:
            self.download_dir.set(download_dir)

    def on_progress_callback(self, stream, chunk, bytes_remaining):
        size = stream.filesize
        downloaded = size - bytes_remaining
        percent = (downloaded / size) * 100
        msg = f"已下載 {downloaded / (1024 * 1024):.2f} MB / {size / (1024 * 1024):.2f} MB ({percent:.2f}%)"
        self.status_label.config(text=msg)
        self.master.update()

    def update_quality_options(self):
        url = self.url_entry.get()
        if not url:
            return
        yt = YouTube(url)
        streams = yt.streams.filter(progressive=False)
        quality_options = []

        for stream in streams:
            if stream.resolution and stream.resolution not in quality_options:
                quality_options.append(stream.resolution)

        # 將品質選項按照解析度大小排序
        quality_options.sort(key=lambda x: -int(x[:-1]))

        self.quality_menu['menu'].delete(0, 'end')
        for option in ["自動（最高畫質）"] + quality_options:
            self.quality_menu['menu'].add_command(label=option, command=tk._setit(self.quality_var, option))

    def download_video(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("錯誤", "請輸入影片網址")
            return

        try:
            yt = YouTube(url, on_progress_callback=self.on_progress_callback)
        except Exception as e:
            messagebox.showerror("錯誤", "發生錯誤：" + str(e))
            return

        quality = self.quality_var.get()
        if quality == "自動（最高畫質）":
            stream = yt.streams.get_highest_resolution()
        else:
            stream = yt.streams.filter(res=quality, progressive=True).first()

        download_dir = self.download_dir.get()
        if download_dir == "選擇下載位置":
            messagebox.showerror("錯誤", "請選擇下載位置")
            return

        stream.download(download_dir)
        self.status_label.config(text="下載完成！")


root = tk.Tk()
yt_downloader = YouTubeDownloader(root)
url_trace = tk.StringVar()
url_trace.trace("w", lambda name, index, mode, url=url_trace: yt_downloader.update_quality_options())
yt_downloader.url_entry.config(textvariable=url_trace)
url_trace = tk.StringVar()
url_trace.trace("w", lambda name, index, mode, url=url_trace: yt_downloader.update_quality_options())
yt_downloader.url_entry.config(textvariable=url_trace)

root.mainloop()
