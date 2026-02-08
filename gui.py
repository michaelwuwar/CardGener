#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CardGener GUI应用
提供友好的图形界面，集成所有功能
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import threading
from pathlib import Path
import json
import shutil


class CardGeneratorGUI:
    """卡牌生成器GUI主类"""

    def __init__(self, root):
        """初始化GUI"""
        self.root = root
        self.root.title("CardGener - 卡牌批量生成工具")
        self.root.geometry("900x700")

        # 设置样式
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # 创建主界面
        self.create_widgets()

        # 设置持久化文件路径（存放到用户主目录隐藏文件）
        self.settings_path = Path.home() / ".cardgener_gui_settings.json"

        # 尝试加载先前的设置
        try:
            self.load_settings()
        except Exception:
            # 忽略加载错误，继续使用默认值
            pass

        # 在关闭窗口时提供保存选项
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # 状态变量
        self.is_processing = False

    def create_widgets(self):
        """创建界面组件"""
        # 菜单：包含设置的保存/加载
        menubar = tk.Menu(self.root)
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="保存设置", command=self.save_settings)
        settings_menu.add_command(label="加载设置", command=self.load_settings)
        settings_menu.add_separator()
        settings_menu.add_command(label="重置为默认", command=self._reset_settings_prompt)
        menubar.add_cascade(label="设置", menu=settings_menu)
        self.root.config(menu=menubar)
        # 创建笔记本（选项卡）
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # 选项卡1: 基础生成
        self.tab_basic = ttk.Frame(notebook)
        notebook.add(self.tab_basic, text="基础生成")
        self.create_basic_tab()

        # 选项卡2: 批量导入
        self.tab_import = ttk.Frame(notebook)
        notebook.add(self.tab_import, text="CardConjurer导入")
        self.create_import_tab()

        # 选项卡3: 图片拼接
        self.tab_stitch = ttk.Frame(notebook)
        notebook.add(self.tab_stitch, text="图片拼接")
        self.create_stitch_tab()

        # 选项卡4: AI生成
        self.tab_ai = ttk.Frame(notebook)
        notebook.add(self.tab_ai, text="AI图片生成")
        self.create_ai_tab()

        # 状态栏
        self.status_bar = ttk.Label(self.root, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_basic_tab(self):
        """创建基础生成选项卡"""
        frame = ttk.LabelFrame(self.tab_basic, text="从Excel/CSV生成JSON", padding=20)
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        # 输入文件
        ttk.Label(frame, text="输入文件:").grid(row=0, column=0, sticky='w', pady=5)
        self.basic_input_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.basic_input_var, width=50).grid(row=0, column=1, pady=5, padx=5)
        ttk.Button(frame, text="浏览...", command=self.browse_input_file).grid(row=0, column=2, pady=5)

        # 输出目录
        ttk.Label(frame, text="输出目录:").grid(row=1, column=0, sticky='w', pady=5)
        self.basic_output_var = tk.StringVar(value="output")
        ttk.Entry(frame, textvariable=self.basic_output_var, width=50).grid(row=1, column=1, pady=5, padx=5)
        ttk.Button(frame, text="浏览...", command=self.browse_output_dir).grid(row=1, column=2, pady=5)

        # 模板文件
        ttk.Label(frame, text="模板文件:").grid(row=2, column=0, sticky='w', pady=5)
        self.basic_template_var = tk.StringVar(value="template.json")
        ttk.Entry(frame, textvariable=self.basic_template_var, width=50).grid(row=2, column=1, pady=5, padx=5)
        ttk.Button(frame, text="浏览...", command=self.browse_template_file).grid(row=2, column=2, pady=5)

        # 生成按钮
        ttk.Button(frame, text="生成JSON文件", command=self.run_basic_generation, style='Accent.TButton').grid(
            row=3, column=0, columnspan=3, pady=20
        )

        # 日志输出
        ttk.Label(frame, text="日志:").grid(row=4, column=0, sticky='nw', pady=5)
        self.basic_log = scrolledtext.ScrolledText(frame, height=15, width=70)
        self.basic_log.grid(row=5, column=0, columnspan=3, pady=5)

    def create_import_tab(self):
        """创建CardConjurer导入选项卡"""
        frame = ttk.LabelFrame(self.tab_import, text="批量导入到CardConjurer", padding=20)
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        # JSON目录
        ttk.Label(frame, text="JSON目录:").grid(row=0, column=0, sticky='w', pady=5)
        self.import_json_dir_var = tk.StringVar(value="output")
        ttk.Entry(frame, textvariable=self.import_json_dir_var, width=50).grid(row=0, column=1, pady=5, padx=5)
        ttk.Button(frame, text="浏览...", command=self.browse_json_dir).grid(row=0, column=2, pady=5)

        # 下载目录
        ttk.Label(frame, text="下载目录:").grid(row=1, column=0, sticky='w', pady=5)
        self.import_download_var = tk.StringVar(value="downloaded_images")
        ttk.Entry(frame, textvariable=self.import_download_var, width=50).grid(row=1, column=1, pady=5, padx=5)
        ttk.Button(frame, text="浏览...", command=self.browse_download_dir).grid(row=1, column=2, pady=5)

        # 叠加目录（可选）
        ttk.Label(frame, text="叠加目录: ").grid(row=2, column=0, sticky='w', pady=5)
        self.import_overlay_dir_var = tk.StringVar(value="")
        ttk.Entry(frame, textvariable=self.import_overlay_dir_var, width=50).grid(row=2, column=1, pady=5, padx=5)
        ttk.Button(frame, text="浏览...", command=self.browse_overlay_dir).grid(row=2, column=2, pady=5)

        # 无头模式
        self.import_headless_var = tk.BooleanVar(value=False)
        self.import_apply_overlay_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="无头模式运行（后台）", variable=self.import_headless_var).grid(
            row=3, column=0, columnspan=3, sticky='w', pady=5
        )
        ttk.Checkbutton(frame, text="导入后按 JSON bounds 叠加本地艺术图", variable=self.import_apply_overlay_var).grid(
            row=4, column=0, columnspan=3, sticky='w', pady=5
        )
        
        # 导入按钮
        ttk.Button(frame, text="开始导入并下载", command=self.run_import, style='Accent.TButton').grid(
            row=5, column=0, columnspan=3, pady=20
        )

        # 日志输出
        ttk.Label(frame, text="日志:").grid(row=6, column=0, sticky='nw', pady=5)
        self.import_log = scrolledtext.ScrolledText(frame, height=15, width=70)
        self.import_log.grid(row=7, column=0, columnspan=3, pady=5)

    def create_stitch_tab(self):
        """创建图片拼接选项卡"""
        frame = ttk.LabelFrame(self.tab_stitch, text="图片拼接", padding=20)
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        # 输入目录
        ttk.Label(frame, text="图片目录:").grid(row=0, column=0, sticky='w', pady=5)
        self.stitch_input_var = tk.StringVar(value="downloaded_images")
        ttk.Entry(frame, textvariable=self.stitch_input_var, width=50).grid(row=0, column=1, pady=5, padx=5)
        ttk.Button(frame, text="浏览...", command=self.browse_stitch_input).grid(row=0, column=2, pady=5)

        # 输出目录（将作为输出文件夹使用）
        ttk.Label(frame, text="输出目录:").grid(row=1, column=0, sticky='w', pady=5)
        self.stitch_output_var = tk.StringVar(value="tts_decks")
        ttk.Entry(frame, textvariable=self.stitch_output_var, width=50).grid(row=1, column=1, pady=5, padx=5)
        ttk.Button(frame, text="浏览...", command=self.browse_stitch_output).grid(row=1, column=2, pady=5)

        # 行列设置
        settings_frame = ttk.Frame(frame)
        settings_frame.grid(row=2, column=0, columnspan=3, pady=10)

        ttk.Label(settings_frame, text="列数:").pack(side=tk.LEFT, padx=5)
        self.stitch_cols_var = tk.IntVar(value=10)
        ttk.Spinbox(settings_frame, from_=1, to=20, textvariable=self.stitch_cols_var, width=10).pack(side=tk.LEFT, padx=5)

        ttk.Label(settings_frame, text="间距:").pack(side=tk.LEFT, padx=5)
        self.stitch_spacing_var = tk.IntVar(value=0)
        ttk.Spinbox(settings_frame, from_=0, to=50, textvariable=self.stitch_spacing_var, width=10).pack(side=tk.LEFT, padx=5)

        # 缩放预设和自定义宽度
        ttk.Label(settings_frame, text="输出预设: ").pack(side=tk.LEFT, padx=8)
        self.stitch_preset_var = tk.StringVar(value="")
        presets = ['', '4k', '2k', '1080p', '720p']
        ttk.Combobox(settings_frame, textvariable=self.stitch_preset_var, values=presets, width=8, state='readonly').pack(side=tk.LEFT, padx=5)

        ttk.Label(settings_frame, text="目标宽度: ").pack(side=tk.LEFT, padx=5)
        self.stitch_target_width_var = tk.StringVar(value="")
        ttk.Entry(settings_frame, textvariable=self.stitch_target_width_var, width=8).pack(side=tk.LEFT, padx=5)

        ttk.Label(settings_frame, text="每页卡数: ").pack(side=tk.LEFT, padx=5)
        self.stitch_cards_per_sheet_var = tk.IntVar(value=70)
        ttk.Spinbox(settings_frame, from_=1, to=1000, textvariable=self.stitch_cards_per_sheet_var, width=6).pack(side=tk.LEFT, padx=5)

        # TTS模式
        self.stitch_tts_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="TTS模式（10×7，每页70张）", variable=self.stitch_tts_var).grid(
            row=3, column=0, columnspan=3, sticky='w', pady=5
        )

        # 拼接按钮
        ttk.Button(frame, text="开始拼接", command=self.run_stitch, style='Accent.TButton').grid(
            row=4, column=0, columnspan=3, pady=20
        )

        # 日志输出
        ttk.Label(frame, text="日志:").grid(row=5, column=0, sticky='nw', pady=5)
        self.stitch_log = scrolledtext.ScrolledText(frame, height=10, width=70)
        self.stitch_log.grid(row=6, column=0, columnspan=3, pady=5)

    def create_ai_tab(self):
        """创建AI生成选项卡"""
        frame = ttk.LabelFrame(self.tab_ai, text="AI图片生成", padding=20)
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        # JSON目录
        ttk.Label(frame, text="JSON目录:").grid(row=0, column=0, sticky='w', pady=5)
        self.ai_json_dir_var = tk.StringVar(value="output")
        ttk.Entry(frame, textvariable=self.ai_json_dir_var, width=50).grid(row=0, column=1, pady=5, padx=5)
        ttk.Button(frame, text="浏览...", command=self.browse_ai_json_dir).grid(row=0, column=2, pady=5)

        # 输出目录
        ttk.Label(frame, text="输出目录:").grid(row=1, column=0, sticky='w', pady=5)
        self.ai_output_var = tk.StringVar(value="generated_art")
        ttk.Entry(frame, textvariable=self.ai_output_var, width=50).grid(row=1, column=1, pady=5, padx=5)
        ttk.Button(frame, text="浏览...", command=self.browse_ai_output).grid(row=1, column=2, pady=5)

        # API选择
        ttk.Label(frame, text="API类型:").grid(row=2, column=0, sticky='w', pady=5)
        self.ai_api_var = tk.StringVar(value="pollinations")
        api_combo = ttk.Combobox(
            frame,
            textvariable=self.ai_api_var,
            values=["pollinations", "stability", "huggingface", "modelscope", "modelscope_inference"],
            state='readonly',
            width=20,
        )
        api_combo.grid(row=2, column=1, sticky='w', pady=5, padx=5)

        # API Key（隐藏输入）
        ttk.Label(frame, text="API Key:").grid(row=3, column=0, sticky='w', pady=5)
        self.ai_api_key_var = tk.StringVar()
        self.ai_show_key_var = tk.BooleanVar(value=False)
        # 使用 Entry 实例以便后续切换可见性
        self.ai_api_key_entry = ttk.Entry(frame, textvariable=self.ai_api_key_var, width=40, show='*')
        self.ai_api_key_entry.grid(row=3, column=1, pady=5, padx=5)
        ttk.Checkbutton(frame, text="显示", variable=self.ai_show_key_var, command=self.toggle_api_key_visibility).grid(row=3, column=2, pady=5)

        # 模型标识
        ttk.Label(frame, text="模型(model):").grid(row=4, column=0, sticky='w', pady=5)
        self.ai_model_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.ai_model_var, width=40).grid(row=4, column=1, pady=5, padx=5)

        # 宽高与轮询间隔（按独立行排列，避免重叠）
        ttk.Label(frame, text="宽度: ").grid(row=5, column=0, sticky='w', pady=5)
        self.ai_width_var = tk.IntVar(value=1024)
        ttk.Spinbox(frame, from_=64, to=2048, increment=64, textvariable=self.ai_width_var, width=10).grid(row=5, column=1, sticky='w', pady=5, padx=5)

        ttk.Label(frame, text="高度: ").grid(row=6, column=0, sticky='w', pady=5)
        self.ai_height_var = tk.IntVar(value=1024)
        ttk.Spinbox(frame, from_=64, to=2048, increment=64, textvariable=self.ai_height_var, width=10).grid(row=6, column=1, sticky='w', pady=5)

        ttk.Label(frame, text="轮询间隔(s):").grid(row=7, column=0, sticky='w', pady=5)
        self.ai_poll_var = tk.IntVar(value=5)
        ttk.Spinbox(frame, from_=1, to=60, textvariable=self.ai_poll_var, width=8).grid(row=7, column=1, sticky='w', pady=5, padx=5)

        # 跳过已存在图片选项（默认勾选）
        self.ai_skip_existing_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="跳过已存在的图片", variable=self.ai_skip_existing_var).grid(
            row=8, column=0, columnspan=3, sticky='w', pady=5
        )

        # 生成按钮
        ttk.Button(frame, text="生成AI图片", command=self.run_ai_generation, style='Accent.TButton').grid(
            row=9, column=0, columnspan=3, pady=20
        )

        # 日志输出（放在生成按钮下方，独立行）
        ttk.Label(frame, text="日志:").grid(row=10, column=0, sticky='nw', pady=5)
        self.ai_log = scrolledtext.ScrolledText(frame, height=15, width=70)
        self.ai_log.grid(row=11, column=0, columnspan=3, pady=5)

    # 浏览按钮回调函数
    def browse_input_file(self):
        filename = filedialog.askopenfilename(
            title="选择Excel/CSV文件",
            filetypes=[("Excel/CSV", "*.xlsx *.xls *.csv"), ("所有文件", "*.*")]
        )
        if filename:
            self.basic_input_var.set(filename)

    def browse_output_dir(self):
        dirname = filedialog.askdirectory(title="选择输出目录")
        if dirname:
            self.basic_output_var.set(dirname)

    def browse_template_file(self):
        filename = filedialog.askopenfilename(
            title="选择模板文件",
            filetypes=[("JSON", "*.json"), ("所有文件", "*.*")]
        )
        if filename:
            self.basic_template_var.set(filename)

    def browse_json_dir(self):
        dirname = filedialog.askdirectory(title="选择JSON目录")
        if dirname:
            self.import_json_dir_var.set(dirname)

    def browse_download_dir(self):
        dirname = filedialog.askdirectory(title="选择下载目录")
        if dirname:
            self.import_download_var.set(dirname)

    def browse_overlay_dir(self):
        dirname = filedialog.askdirectory(title="选择本地生成艺术图目录")
        if dirname:
            self.import_overlay_dir_var.set(dirname)

    def browse_stitch_input(self):
        dirname = filedialog.askdirectory(title="选择图片目录")
        if dirname:
            self.stitch_input_var.set(dirname)

    def browse_stitch_output(self):
        dirname = filedialog.askdirectory(title="选择输出目录")
        if dirname:
            self.stitch_output_var.set(dirname)

    def browse_ai_json_dir(self):
        dirname = filedialog.askdirectory(title="选择JSON目录")
        if dirname:
            self.ai_json_dir_var.set(dirname)

    def browse_ai_output(self):
        dirname = filedialog.askdirectory(title="选择输出目录")
        if dirname:
            self.ai_output_var.set(dirname)

    def toggle_api_key_visibility(self):
        """切换 AI Key 的可见性（掩码/明文）。"""
        try:
            if self.ai_show_key_var.get():
                self.ai_api_key_entry.config(show='')
            else:
                self.ai_api_key_entry.config(show='*')
        except Exception:
            pass

    # 执行函数
    def run_basic_generation(self):
        """运行基础生成"""
        if self.is_processing:
            messagebox.showwarning("警告", "已有任务正在运行")
            return

        input_file = self.basic_input_var.get()
        output_dir = self.basic_output_var.get()
        template_file = self.basic_template_var.get()

        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("错误", "请选择有效的输入文件")
            return

        self.is_processing = True
        self.status_bar.config(text="正在生成...")
        self.basic_log.delete(1.0, tk.END)

        def task():
            try:
                from card_generator import CardGenerator
                self.log_message(self.basic_log, f"开始生成卡牌...\n")
                self.log_message(self.basic_log, f"输入: {input_file}\n")
                self.log_message(self.basic_log, f"输出: {output_dir}\n")

                generator = CardGenerator(template_file)
                generator.generate_from_excel(input_file, output_dir)

                self.log_message(self.basic_log, f"\n✅ 生成完成！\n")
                self.status_bar.config(text="生成完成")
                messagebox.showinfo("成功", "卡牌生成完成！")

            except Exception as e:
                self.log_message(self.basic_log, f"\n❌ 错误: {str(e)}\n")
                self.status_bar.config(text="生成失败")
                messagebox.showerror("错误", f"生成失败: {str(e)}")

            finally:
                self.is_processing = False

        threading.Thread(target=task, daemon=True).start()

    def run_import(self):
        """运行CardConjurer导入"""
        if self.is_processing:
            messagebox.showwarning("警告", "已有任务正在运行")
            return

        json_dir = self.import_json_dir_var.get()
        download_dir = self.import_download_var.get()
        headless = self.import_headless_var.get()

        # 前置检查: 确保 selenium 可用并提示 chromedriver
        try:
            import selenium  # type: ignore
        except Exception:
            messagebox.showerror("错误", "未检测到 selenium 库。请运行: pip install selenium\n或参阅项目文档安装依赖。")
            return

        if shutil.which('chromedriver') is None:
            proceed = messagebox.askyesno("提示", "未在 PATH 中找到 chromedriver，Selenium 可能无法启动。是否继续尝试？")
            if not proceed:
                return

        if not json_dir or not os.path.exists(json_dir):
            messagebox.showerror("错误", "请选择有效的JSON目录")
            return

        # 收集所有 json 文件
        json_paths = list(Path(json_dir).glob("*.json"))
        if not json_paths:
            messagebox.showerror("错误", f"未在目录中找到JSON文件: {json_dir}")
            return

        self.is_processing = True
        self.status_bar.config(text="正在导入CardConjurer...")
        self.import_log.delete(1.0, tk.END)

        def task():
            try:
                from cardconjurer_automation import CardConjurerAutomation

                self.log_message(self.import_log, f"开始导入 {len(json_paths)} 个JSON 到 CardConjurer\n")
                self.log_message(self.import_log, f"下载目录: {download_dir}\n")
                self.log_message(self.import_log, f"无头模式: {headless}\n")

                automation = CardConjurerAutomation(headless=headless, download_dir=download_dir)
                # batch_import_and_download 接受路径列表
                files = [str(p) for p in json_paths]
                success_count = automation.batch_import_and_download(files)

                self.log_message(self.import_log, f"\n✅ 完成: 成功处理 {success_count}/{len(files)} 张卡牌\n")
                self.status_bar.config(text="导入完成")
                messagebox.showinfo("成功", f"导入完成，成功处理 {success_count}/{len(files)} 张卡牌")

                # 如果用户指定了叠加目录并勾选了叠加选项，则执行叠加（使用 JSON 中的 bounds）
                overlay_dir = self.import_overlay_dir_var.get().strip()
                apply_overlay = bool(self.import_apply_overlay_var.get())
                if overlay_dir and apply_overlay:
                    try:
                        self.log_message(self.import_log, f"\n🎨 开始按 JSON bounds 叠加艺术图（来自: {overlay_dir}）\n")
                        overlayed = automation.overlay_generated_art(overlay_dir, source_dir=download_dir, json_dir=json_dir, inplace=True)
                        self.log_message(self.import_log, f"\n✅ 叠加完成: {overlayed} 张图片已处理\n")
                    except Exception as e:
                        self.log_message(self.import_log, f"\n⚠️ 叠加步骤出错: {e}\n")

            except Exception as e:
                self.log_message(self.import_log, f"\n❌ 错误: {str(e)}\n")
                self.status_bar.config(text="导入失败")
                messagebox.showerror("错误", f"导入失败: {str(e)}")

            finally:
                self.is_processing = False

        threading.Thread(target=task, daemon=True).start()

    def run_stitch(self):
        """运行图片拼接"""
        if self.is_processing:
            messagebox.showwarning("警告", "已有任务正在运行")
            return

        input_dir = self.stitch_input_var.get()
        # 将“输出文件”字段作为输出目录使用（符合用户需求）
        output_dir = self.stitch_output_var.get().strip()

        # 默认输出目录为 input_dir/tts_decks
        if not output_dir:
            output_dir = os.path.join(input_dir, 'tts_decks')

        # 如果用户选择了一个文件路径（有扩展名），则取其父目录作为输出目录
        base, ext = os.path.splitext(output_dir)
        if ext and not os.path.isdir(output_dir):
            output_dir = os.path.dirname(output_dir) or output_dir

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        if not input_dir or not os.path.exists(input_dir):
            messagebox.showerror("错误", "请选择有效的图片目录")
            return

        self.is_processing = True
        self.status_bar.config(text="正在拼接...")
        self.stitch_log.delete(1.0, tk.END)

        def task():
            try:
                from image_stitcher import ImageStitcher

                self.log_message(self.stitch_log, f"开始拼接图片...\n")

                stitcher = ImageStitcher()

                if self.stitch_tts_var.get():
                    # TTS模式：使用输出目录（默认或用户指定）
                    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
                    image_paths = [
                        str(p) for p in Path(input_dir).iterdir()
                        if p.suffix.lower() in image_extensions
                    ]
                    image_paths.sort()

                    preset = self.stitch_preset_var.get() or None
                    target_w = None
                    try:
                        tw = int(self.stitch_target_width_var.get())
                        if tw > 0:
                            target_w = tw
                    except Exception:
                        target_w = None

                    cards_per_sheet = self.stitch_cards_per_sheet_var.get() or 70

                    sheets = stitcher.create_tabletop_simulator_deck(
                        image_paths,
                        str(output_dir),
                        cards_per_sheet=cards_per_sheet,
                        cols=10,
                        preset=preset,
                        target_width=target_w,
                    )
                    self.log_message(self.stitch_log, f"\n✅ 生成了 {len(sheets)} 张TTS卡牌页，保存在: {output_dir}\n")
                else:
                    # 普通模式：也写入输出目录，支持多张结果
                    cols = self.stitch_cols_var.get()
                    spacing = self.stitch_spacing_var.get()
                    preset = self.stitch_preset_var.get() or None
                    target_w = None
                    try:
                        tw = int(self.stitch_target_width_var.get())
                        if tw > 0:
                            target_w = tw
                    except Exception:
                        target_w = None

                    cards_per_sheet = self.stitch_cards_per_sheet_var.get() or None

                    stitcher.auto_stitch(
                        input_dir,
                        output_dir,
                        max_cols=cols,
                        spacing=spacing,
                        cards_per_sheet=cards_per_sheet,
                        preset=preset,
                        target_width=target_w,
                    )
                    self.log_message(self.stitch_log, f"\n✅ 拼接完成，输出保存在: {output_dir}\n")

                self.status_bar.config(text="拼接完成")
                messagebox.showinfo("成功", "图片拼接完成！")

            except Exception as e:
                self.log_message(self.stitch_log, f"\n❌ 错误: {str(e)}\n")
                self.status_bar.config(text="拼接失败")
                messagebox.showerror("错误", f"拼接失败: {str(e)}")

            finally:
                self.is_processing = False

        threading.Thread(target=task, daemon=True).start()

    def run_ai_generation(self):
        """运行AI图片生成"""
        if self.is_processing:
            messagebox.showwarning("警告", "已有任务正在运行")
            return

        json_dir = self.ai_json_dir_var.get()
        output_dir = self.ai_output_var.get()
        api_type = self.ai_api_var.get()

        if not json_dir or not os.path.exists(json_dir):
            messagebox.showerror("错误", "请选择有效的JSON目录")
            return

        self.is_processing = True
        self.status_bar.config(text="正在生成AI图片...")
        self.ai_log.delete(1.0, tk.END)

        def task():
            try:
                from ai_image_generator import AIImageGenerator

                self.log_message(self.ai_log, f"开始AI图片生成...\n")
                self.log_message(self.ai_log, f"API: {api_type}\n")

                generator = AIImageGenerator(api_type=api_type)

                # 传递可视化设置到 generator
                api_key = self.ai_api_key_var.get().strip()
                model = self.ai_model_var.get().strip()
                width = int(self.ai_width_var.get())
                height = int(self.ai_height_var.get())
                poll = int(self.ai_poll_var.get())

                if api_key:
                    generator.api_key = api_key
                    self.log_message(self.ai_log, f"使用 API Key: {api_key[:8]}...\n")
                if model:
                    generator.api_model = model
                    self.log_message(self.ai_log, f"使用模型: {model}\n")

                # 将轮询间隔设置到 generator（用于 modelscope_inference）
                generator.poll_interval = poll

                self.log_message(self.ai_log, f"宽度×高度: {width}×{height}\n")

                # 是否跳过已存在的图片（来自界面勾选）
                skip_existing = getattr(self, 'ai_skip_existing_var', tk.BooleanVar(value=True)).get()

                count = generator.enhance_existing_cards(
                    json_dir,
                    output_dir,
                    update_json=False,
                    width=width,
                    height=height,
                    poll_interval=poll,
                    skip_if_exists=skip_existing,
                )

                self.log_message(self.ai_log, f"\n✅ 成功生成 {count} 张图片\n")
                self.status_bar.config(text="AI生成完成")
                messagebox.showinfo("成功", f"成功生成 {count} 张AI图片！")

            except Exception as e:
                self.log_message(self.ai_log, f"\n❌ 错误: {str(e)}\n")
                self.status_bar.config(text="AI生成失败")
                messagebox.showerror("错误", f"AI生成失败: {str(e)}")

            finally:
                self.is_processing = False

        threading.Thread(target=task, daemon=True).start()

    def log_message(self, log_widget, message):
        """添加日志消息"""
        log_widget.insert(tk.END, message)
        log_widget.see(tk.END)
        log_widget.update()

    def get_settings_dict(self):
        """收集当前界面设置为字典"""
        return {
            "geometry": self.root.geometry(),
            "basic_input": self.basic_input_var.get(),
            "basic_output": self.basic_output_var.get(),
            "basic_template": self.basic_template_var.get(),
            "import_json_dir": self.import_json_dir_var.get(),
            "import_download_dir": self.import_download_var.get(),
            "import_headless": bool(self.import_headless_var.get()),
            "import_overlay_dir": self.import_overlay_dir_var.get(),
            "import_apply_overlay": bool(self.import_apply_overlay_var.get()),
            "stitch_input": self.stitch_input_var.get(),
            "stitch_output": self.stitch_output_var.get(),
            "stitch_cols": int(self.stitch_cols_var.get()),
            "stitch_spacing": int(self.stitch_spacing_var.get()),
            "stitch_preset": self.stitch_preset_var.get(),
            "stitch_target_width": self.stitch_target_width_var.get(),
            "stitch_cards_per_sheet": int(self.stitch_cards_per_sheet_var.get()),
            "stitch_tts": bool(self.stitch_tts_var.get()),
            "ai_json_dir": self.ai_json_dir_var.get(),
            "ai_output": self.ai_output_var.get(),
            "ai_api": self.ai_api_var.get(),
            "ai_api_key": self.ai_api_key_var.get(),
            "ai_model": self.ai_model_var.get(),
            "ai_width": int(self.ai_width_var.get()),
            "ai_height": int(self.ai_height_var.get()),
            "ai_poll": int(self.ai_poll_var.get()),
            "ai_skip_existing": bool(self.ai_skip_existing_var.get()),
        }

    def apply_settings(self, data: dict):
        """应用设置字典到界面控件"""
        try:
            geom = data.get("geometry")
            if geom:
                try:
                    self.root.geometry(geom)
                except Exception:
                    pass

            if "basic_input" in data:
                self.basic_input_var.set(data.get("basic_input") or "")
            if "basic_output" in data:
                self.basic_output_var.set(data.get("basic_output") or "output")
            if "basic_template" in data:
                self.basic_template_var.set(data.get("basic_template") or "template.json")

            if "import_json_dir" in data:
                self.import_json_dir_var.set(data.get("import_json_dir") or "output")
            if "import_download_dir" in data:
                self.import_download_var.set(data.get("import_download_dir") or "downloaded_images")
            if "import_headless" in data:
                self.import_headless_var.set(bool(data.get("import_headless")))
            if "import_overlay_dir" in data:
                try:
                    self.import_overlay_dir_var.set(data.get("import_overlay_dir") or "")
                except Exception:
                    pass
            if "import_apply_overlay" in data:
                try:
                    self.import_apply_overlay_var.set(bool(data.get("import_apply_overlay")))
                except Exception:
                    pass

            if "stitch_input" in data:
                self.stitch_input_var.set(data.get("stitch_input") or "downloaded_images")
            if "stitch_output" in data:
                self.stitch_output_var.set(data.get("stitch_output") or "tts_decks")
            if "stitch_cols" in data:
                try:
                    self.stitch_cols_var.set(int(data.get("stitch_cols")))
                except Exception:
                    pass
            if "stitch_spacing" in data:
                try:
                    self.stitch_spacing_var.set(int(data.get("stitch_spacing")))
                except Exception:
                    pass
            if "stitch_preset" in data:
                self.stitch_preset_var.set(data.get("stitch_preset") or "")
            if "stitch_target_width" in data:
                self.stitch_target_width_var.set(data.get("stitch_target_width") or "")
            if "stitch_cards_per_sheet" in data:
                try:
                    self.stitch_cards_per_sheet_var.set(int(data.get("stitch_cards_per_sheet")))
                except Exception:
                    pass
            if "stitch_tts" in data:
                self.stitch_tts_var.set(bool(data.get("stitch_tts")))

            if "ai_json_dir" in data:
                self.ai_json_dir_var.set(data.get("ai_json_dir") or "output")
            if "ai_output" in data:
                self.ai_output_var.set(data.get("ai_output") or "generated_art")
            if "ai_api" in data:
                self.ai_api_var.set(data.get("ai_api") or "pollinations")
            if "ai_api_key" in data:
                self.ai_api_key_var.set(data.get("ai_api_key") or "")
            if "ai_model" in data:
                self.ai_model_var.set(data.get("ai_model") or "")
            if "ai_width" in data:
                try:
                    self.ai_width_var.set(int(data.get("ai_width")))
                except Exception:
                    pass
            if "ai_height" in data:
                try:
                    self.ai_height_var.set(int(data.get("ai_height")))
                except Exception:
                    pass
            if "ai_poll" in data:
                try:
                    self.ai_poll_var.set(int(data.get("ai_poll")))
                except Exception:
                    pass
            if "ai_skip_existing" in data:
                try:
                    self.ai_skip_existing_var.set(bool(data.get("ai_skip_existing")))
                except Exception:
                    pass
        except Exception:
            # 忽略应用过程中的任何问题
            pass

    def save_settings(self):
        """将当前设置保存到磁盘"""
        try:
            data = self.get_settings_dict()
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("保存", f"设置已保存到: {self.settings_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败: {str(e)}")

    def load_settings(self):
        """从磁盘加载设置并应用到界面"""
        if not hasattr(self, 'settings_path'):
            self.settings_path = Path.home() / ".cardgener_gui_settings.json"

        if not self.settings_path.exists():
            # 如果由用户手动触发加载，提示不存在
            if threading.current_thread().name != 'MainThread':
                return
            messagebox.showwarning("加载", f"未找到设置文件: {self.settings_path}")
            return

        try:
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.apply_settings(data)
            # 成功加载时在状态栏显示短消息
            try:
                self.status_bar.config(text="已加载设置")
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("错误", f"加载设置失败: {str(e)}")

    def _reset_settings_prompt(self):
        if messagebox.askyesno("重置", "是否重置为默认设置（不会删除已保存文件）？"):
            # 通过应用空字典还原到默认控件初始值
            self.apply_settings({})
            messagebox.showinfo("重置", "界面已重置为默认值。")

    def on_close(self):
        """关闭窗口前询问是否保存设置，然后退出"""
        try:
            if messagebox.askyesno("退出", "是否保存当前设置？"):
                try:
                    self.save_settings()
                except Exception:
                    pass
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            try:
                sys.exit(0)
            except Exception:
                pass


def main():
    """主函数"""
    root = tk.Tk()
    app = CardGeneratorGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
