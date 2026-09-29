import customtkinter as ctk
import pymupdf
import os
import re
import threading
from tkinter import filedialog, messagebox

# 设置 customtkinter 的外观模式和默认颜色主题
ctk.set_appearance_mode("System")  # 跟随系统: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # 主题: "blue", "green", "dark-blue"


class PDF2ImageApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PDF 转图片工具")
        self.geometry("600x720")
        self.minsize(550, 650)

        # 状态变量
        self.pdf_path = ctk.StringVar(value="未选择 PDF 文件")
        self.output_dir = ctk.StringVar(value="未选择输出目录")
        self.convert_mode = ctk.StringVar(value="all")
        self.page_input = ctk.StringVar(value="")
        self.dpi_option = ctk.StringVar(value="2x (144 DPI)")
        self.is_converting = False

        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # 1. 标题
        self.title_label = ctk.CTkLabel(self, text="PDF 转图片工具", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # 2. 文件选择区
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.file_frame.grid_columnconfigure(0, weight=1)

        self.pdf_label = ctk.CTkLabel(self.file_frame, textvariable=self.pdf_path, anchor="w")
        self.pdf_label.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        self.btn_select_pdf = ctk.CTkButton(self.file_frame, text="选择 PDF", width=120, command=self.select_pdf)
        self.btn_select_pdf.grid(row=0, column=1, padx=(0, 15), pady=15)

        # 3. 参数设置区
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.settings_frame.grid_columnconfigure(1, weight=1)

        # 转换模式
        ctk.CTkLabel(self.settings_frame, text="转换范围:").grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        self.radio_all = ctk.CTkRadioButton(self.settings_frame, text="全部页面", variable=self.convert_mode,
                                            value="all", command=self.toggle_page_input)
        self.radio_all.grid(row=0, column=1, padx=15, pady=(15, 5), sticky="w")
        self.radio_custom = ctk.CTkRadioButton(self.settings_frame, text="指定页码", variable=self.convert_mode,
                                               value="custom", command=self.toggle_page_input)
        self.radio_custom.grid(row=0, column=2, padx=15, pady=(15, 5), sticky="w")

        # 页码输入
        ctk.CTkLabel(self.settings_frame, text="指定页码:").grid(row=1, column=0, padx=15, pady=5, sticky="w")
        self.entry_pages = ctk.CTkEntry(self.settings_frame, placeholder_text="例: 1,3,5-10",
                                        textvariable=self.page_input, state="disabled")
        self.entry_pages.grid(row=1, column=1, columnspan=2, padx=15, pady=5, sticky="ew")

        # 清晰度选择
        ctk.CTkLabel(self.settings_frame, text="图片清晰度:").grid(row=2, column=0, padx=15, pady=(5, 15), sticky="w")
        self.combo_dpi = ctk.CTkComboBox(self.settings_frame,
                                         values=["1x (72 DPI)", "2x (144 DPI)", "3x (216 DPI)", "4x (288 DPI)"],
                                         variable=self.dpi_option, state="readonly")
        self.combo_dpi.grid(row=2, column=1, columnspan=2, padx=15, pady=(5, 15), sticky="ew")

        # 4. 输出目录与操作区
        self.output_frame = ctk.CTkFrame(self)
        self.output_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.output_frame.grid_columnconfigure(0, weight=1)

        self.dir_label = ctk.CTkLabel(self.output_frame, textvariable=self.output_dir, anchor="w")
        self.dir_label.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        self.btn_select_dir = ctk.CTkButton(self.output_frame, text="选择输出目录", width=120,
                                            command=self.select_output_dir)
        self.btn_select_dir.grid(row=0, column=1, padx=(0, 15), pady=15)

        # 5. 进度与日志区
        self.progress_frame = ctk.CTkFrame(self)
        self.progress_frame.grid(row=4, column=0, padx=20, pady=10, sticky="nsew")
        self.progress_frame.grid_columnconfigure(0, weight=1)
        self.progress_frame.grid_rowconfigure(1, weight=1)

        self.progressbar = ctk.CTkProgressBar(self.progress_frame, mode="determinate")
        self.progressbar.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="ew")
        self.progressbar.set(0)

        self.log_text = ctk.CTkTextbox(self.progress_frame, state="disabled",
                                       font=ctk.CTkFont(family="Consolas", size=12))
        self.log_text.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")

        # 6. 底部按钮
        self.btn_start = ctk.CTkButton(self, text="开始转换", height=40, font=ctk.CTkFont(size=16, weight="bold"),
                                       command=self.start_conversion)
        self.btn_start.grid(row=5, column=0, padx=20, pady=(10, 20), sticky="ew")

    def toggle_page_input(self):
        if self.convert_mode.get() == "custom":
            self.entry_pages.configure(state="normal")
        else:
            self.entry_pages.configure(state="disabled")

    def select_pdf(self):
        path = filedialog.askopenfilename(title="选择 PDF 文件", filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.pdf_path.set(path)
            self.log_msg(f"已选择 PDF: {os.path.basename(path)}")

    def select_output_dir(self):
        path = filedialog.askdirectory(title="选择输出目录")
        if path:
            self.output_dir.set(path)
            self.log_msg(f"输出目录: {path}")

    def log_msg(self, msg):
        """线程安全的日志输出"""

        def _update():
            self.log_text.configure(state="normal")
            self.log_text.insert("end", msg + "\n")
            self.log_text.see("end")
            self.log_text.configure(state="disabled")

        self.after(0, _update)

    def update_progress(self, value):
        """线程安全的进度条更新"""
        self.after(0, lambda: self.progressbar.set(value))

    def parse_page_ranges(self, page_str, total_pages):
        """解析页码字符串，如 '1,3,5-10'"""
        pages = set()
        parts = page_str.replace(' ', '').split(',')
        for part in parts:
            if not part:
                continue
            if '-' in part:
                match = re.match(r'^(\d+)-(\d+)$', part)
                if match:
                    start, end = int(match.group(1)), int(match.group(2))
                    for i in range(start, end + 1):
                        if 1 <= i <= total_pages:
                            pages.add(i - 1)  # PyMuPDF 使用 0-based 索引
            else:
                if part.isdigit():
                    i = int(part)
                    if 1 <= i <= total_pages:
                        pages.add(i - 1)
        return sorted(list(pages))

    def start_conversion(self):
        if self.is_converting:
            return

        pdf_path = self.pdf_path.get()
        out_dir = self.output_dir.get()

        if not os.path.isfile(pdf_path):
            messagebox.showerror("错误", "请先选择有效的 PDF 文件！")
            return
        if not os.path.isdir(out_dir):
            messagebox.showerror("错误", "请先选择有效的输出目录！")
            return

        # 获取缩放比例
        dpi_str = self.dpi_option.get()
        zoom = float(dpi_str.split('x')[0])

        # 转换线程
        self.is_converting = True
        self.btn_start.configure(state="disabled", text="转换中...")
        self.progressbar.set(0)

        thread = threading.Thread(target=self.conversion_worker, args=(pdf_path, out_dir, zoom))
        thread.daemon = True
        thread.start()

    def conversion_worker(self, pdf_path, out_dir, zoom):
        try:
            # 使用新的 pymupdf 接口打开文档
            doc = pymupdf.open(pdf_path)
            total_pages = len(doc)
            self.log_msg(f"PDF 加载成功，共 {total_pages} 页。")

            # 确定要转换的页码
            if self.convert_mode.get() == "all":
                pages_to_convert = list(range(total_pages))
                self.log_msg("模式: 转换全部页面")
            else:
                page_str = self.page_input.get()
                if not page_str:
                    self.log_msg("错误: 指定页码模式下，页码输入不能为空！")
                    self.finish_conversion(False)
                    return
                pages_to_convert = self.parse_page_ranges(page_str, total_pages)
                if not pages_to_convert:
                    self.log_msg("错误: 未解析到有效的页码，请检查输入格式！")
                    self.finish_conversion(False)
                    return
                self.log_msg(f"模式: 转换指定页码 {len(pages_to_convert)} 页")

            self.log_msg(f"清晰度设置: {zoom}x 缩放")

            mat = pymupdf.Matrix(zoom, zoom)
            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

            for idx, page_num in enumerate(pages_to_convert):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=mat)

                # 生成输出文件名
                out_file = os.path.join(out_dir, f"{pdf_name}_page_{page_num + 1}.png")
                pix.save(out_file)

                # 更新进度
                progress = (idx + 1) / len(pages_to_convert)
                self.update_progress(progress)
                self.log_msg(f"已保存: {os.path.basename(out_file)}")

            doc.close()
            self.log_msg("========== 转换完成 ==========")
            self.finish_conversion(True)

        except Exception as e:
            self.log_msg(f"发生错误: {str(e)}")
            self.finish_conversion(False)

    def finish_conversion(self, success):
        def _update_ui():
            self.is_converting = False
            self.btn_start.configure(state="normal", text="开始转换")
            if success:
                self.progressbar.set(1.0)
                messagebox.showinfo("完成", "PDF 转图片任务已成功完成！")

        self.after(0, _update_ui)


if __name__ == "__main__":
    app = PDF2ImageApp()
    app.mainloop()