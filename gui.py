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

        # 状态变量
        self.is_processing = False

    def create_widgets(self):
        """创建界面组件"""
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

        # 无头模式
        self.import_headless_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="无头模式运行（后台）", variable=self.import_headless_var).grid(
            row=2, column=0, columnspan=3, sticky='w', pady=5
        )

        # 导入按钮
        ttk.Button(frame, text="开始导入并下载", command=self.run_import, style='Accent.TButton').grid(
            row=3, column=0, columnspan=3, pady=20
        )

        # 日志输出
        ttk.Label(frame, text="日志:").grid(row=4, column=0, sticky='nw', pady=5)
        self.import_log = scrolledtext.ScrolledText(frame, height=15, width=70)
        self.import_log.grid(row=5, column=0, columnspan=3, pady=5)

    def create_stitch_tab(self):
        """创建图片拼接选项卡"""
        frame = ttk.LabelFrame(self.tab_stitch, text="图片拼接", padding=20)
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        # 输入目录
        ttk.Label(frame, text="图片目录:").grid(row=0, column=0, sticky='w', pady=5)
        self.stitch_input_var = tk.StringVar(value="downloaded_images")
        ttk.Entry(frame, textvariable=self.stitch_input_var, width=50).grid(row=0, column=1, pady=5, padx=5)
        ttk.Button(frame, text="浏览...", command=self.browse_stitch_input).grid(row=0, column=2, pady=5)

        # 输出文件
        ttk.Label(frame, text="输出文件:").grid(row=1, column=0, sticky='w', pady=5)
        self.stitch_output_var = tk.StringVar(value="stitched_output.png")
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
        api_combo = ttk.Combobox(frame, textvariable=self.ai_api_var, values=["pollinations", "stability"], state='readonly', width=20)
        api_combo.grid(row=2, column=1, sticky='w', pady=5, padx=5)

        # 生成按钮
        ttk.Button(frame, text="生成AI图片", command=self.run_ai_generation, style='Accent.TButton').grid(
            row=3, column=0, columnspan=3, pady=20
        )

        # 日志输出
        ttk.Label(frame, text="日志:").grid(row=4, column=0, sticky='nw', pady=5)
        self.ai_log = scrolledtext.ScrolledText(frame, height=15, width=70)
        self.ai_log.grid(row=5, column=0, columnspan=3, pady=5)

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

    def browse_stitch_input(self):
        dirname = filedialog.askdirectory(title="选择图片目录")
        if dirname:
            self.stitch_input_var.set(dirname)

    def browse_stitch_output(self):
        filename = filedialog.asksaveasfilename(
            title="保存拼接图片",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("所有文件", "*.*")]
        )
        if filename:
            self.stitch_output_var.set(filename)

    def browse_ai_json_dir(self):
        dirname = filedialog.askdirectory(title="选择JSON目录")
        if dirname:
            self.ai_json_dir_var.set(dirname)

    def browse_ai_output(self):
        dirname = filedialog.askdirectory(title="选择输出目录")
        if dirname:
            self.ai_output_var.set(dirname)

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
        output_file = self.stitch_output_var.get()

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
                    # TTS模式
                    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
                    image_paths = [
                        str(p) for p in Path(input_dir).iterdir()
                        if p.suffix.lower() in image_extensions
                    ]
                    image_paths.sort()

                    output_dir = Path(output_file).parent / 'tts_decks'
                    sheets = stitcher.create_tabletop_simulator_deck(image_paths, str(output_dir))
                    self.log_message(self.stitch_log, f"\n✅ 生成了 {len(sheets)} 张TTS卡牌页\n")
                else:
                    # 普通模式
                    cols = self.stitch_cols_var.get()
                    spacing = self.stitch_spacing_var.get()
                    stitcher.auto_stitch(input_dir, output_file, max_cols=cols, spacing=spacing)
                    self.log_message(self.stitch_log, f"\n✅ 拼接完成: {output_file}\n")

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
                count = generator.enhance_existing_cards(json_dir, output_dir, update_json=True)

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


def main():
    """主函数"""
    root = tk.Tk()
    app = CardGeneratorGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
