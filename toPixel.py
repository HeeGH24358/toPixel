import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np


class PixelArtApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎨 K-Means 智能像素画生成器")
        self.root.geometry("1350x780")
        self.root.resizable(False, False)
        self.root.configure(bg="#f7f8fa")

        style = ttk.Style()
        style.configure(".", bg="#f7f8fa", font=("微软雅黑", 10))
        style.configure("Card.TFrame", background="#ffffff", relief="flat")
        style.configure("Title.TLabel", font=("微软雅黑", 14, "bold"), background="#ffffff")
        style.configure("Button.TButton", font=("微软雅黑", 10), padding=6)

        self.original_w = 0
        self.original_h = 0
        self.cropped_img = None
        self.preview_img = None
        self.final_pixel_img = None
        self.tk_img_original = None
        self.tk_img_preview = None

        left_frame = ttk.Frame(root, width=480, height=750, style="Card.TFrame")
        left_frame.pack(side=tk.LEFT, padx=15, pady=15)
        left_frame.pack_propagate(False)

        ttk.Label(left_frame, text="🖼️ 原始图片", style="Title.TLabel").pack(pady=12)
        self.canvas_original = tk.Canvas(left_frame, bg="#ffffff", width=400, height=400, bd=0, relief="flat",
                                         highlightthickness=1, highlightbackground="#e6e6e6")
        self.canvas_original.pack(pady=8)

        self.size_label = ttk.Label(left_frame, text="图片尺寸：未上传", background="#ffffff")
        self.size_label.pack(pady=4)

        ttk.Label(left_frame, text="K 值（颜色数量）", background="#ffffff").pack(pady=2)
        self.k_entry = ttk.Entry(left_frame, width=18, font=("微软雅黑", 11))
        self.k_entry.insert(0, "8")
        self.k_entry.pack(pady=2)

        ttk.Label(left_frame, text="像素化尺寸", background="#ffffff").pack(pady=2)
        self.pixel_entry = ttk.Entry(left_frame, width=18, font=("微软雅黑", 11))
        self.pixel_entry.insert(0, "16")
        self.pixel_entry.pack(pady=2)

        btn_frame = ttk.Frame(left_frame, style="Card.TFrame")
        btn_frame.pack(pady=12, fill=tk.X, padx=50)
        ttk.Button(btn_frame, text="📁 选择图片", command=self.load_image, style="Button.TButton").pack(pady=4,
                                                                                                       fill=tk.X)
        ttk.Button(btn_frame, text="✨ 生成像素画", command=self.make_pixel_art, style="Button.TButton").pack(pady=4,
                                                                                                             fill=tk.X)

        mid_frame = ttk.Frame(root, width=480, height=750, style="Card.TFrame")
        mid_frame.pack(side=tk.LEFT, padx=15, pady=15)
        mid_frame.pack_propagate(False)

        ttk.Label(mid_frame, text="🎯 像素画预览", style="Title.TLabel").pack(pady=12)
        self.canvas_preview = tk.Canvas(mid_frame, bg="#ffffff", width=400, height=400, bd=0, relief="flat",
                                        highlightthickness=1, highlightbackground="#e6e6e6")
        self.canvas_preview.pack(pady=8)

        ttk.Separator(mid_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=12, padx=50)
        ttk.Label(mid_frame, text="🛠️ 图像编辑", background="#ffffff", font=("微软雅黑", 12, "bold")).pack()

        btn_edit = ttk.Frame(mid_frame, style="Card.TFrame")
        btn_edit.pack(pady=8, fill=tk.X, padx=50)
        ttk.Button(btn_edit, text="🔍 背景透明", command=self.auto_cut_person).pack(pady=3, fill=tk.X)
        ttk.Button(btn_edit, text="🖌️ 白色描边", command=self.add_white_border).pack(pady=3, fill=tk.X)
        ttk.Button(btn_edit, text="⚫ 转为灰度", command=self.to_gray).pack(pady=3, fill=tk.X)

        ttk.Button(mid_frame, text="💾 保存 PNG", command=self.save_image, style="Button.TButton").pack(pady=12,
                                                                                                       fill=tk.X,
                                                                                                       padx=50)

        right_frame = ttk.Frame(root, width=280, height=750, style="Card.TFrame")
        right_frame.pack(side=tk.LEFT, padx=15, pady=15)
        right_frame.pack_propagate(False)

        ttk.Label(right_frame, text="📝 操作日志", style="Title.TLabel").pack(pady=12)
        self.info_text = tk.Text(right_frame, height=42, width=28, font=("Consolas", 9), bg="#fafbfc", relief="flat",
                                 bd=0)
        self.info_text.pack(padx=10, pady=4)
        self.info_text.insert(tk.END, "✅ 等待上传图片\n")

    def log(self, msg):
        self.info_text.insert(tk.END, msg + "\n")
        self.info_text.see(tk.END)

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("图片", "*.jpg *.jpeg *.png")])
        if not path:
            return
        img = Image.open(path).convert("RGBA")
        w, h = img.size
        self.original_w = w
        self.original_h = h
        self.size_label.config(text=f"图片尺寸：{w}×{h}")

        # 取消裁剪，保留原图完整比例
        self.cropped_img = img.copy()

        # 左侧预览：等比例缩到400画布内
        disp = self.cropped_img.copy()
        disp.thumbnail((400, 400))
        self.tk_img_original = ImageTk.PhotoImage(disp)
        self.canvas_original.delete("all")
        self.canvas_original.create_image(200, 200, image=self.tk_img_original)
        self.preview_img = None
        self.log(f"✅ 已加载：{w}×{h}")

    def make_pixel_art(self):
        if self.cropped_img is None:
            self.log("❌ 请先上传图片")
            return

        try:
            K = int(self.k_entry.get())
            K = max(2, min(64, K))
        except:
            K = 8

        try:
            pixel_size = int(self.pixel_entry.get())
            pixel_size = max(2, pixel_size)
        except:
            pixel_size = 16

        self.log(f"🎯 处理中：K={K}，像素尺寸={pixel_size}")

        img_rgb = self.cropped_img.convert("RGB")
        img_np = np.array(img_rgb)
        Z = img_np.reshape((-1, 3))
        Z = np.float32(Z)

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, label, center = cv2.kmeans(Z, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        center = np.uint8(center)
        res = center[label.flatten()]
        quantized_img = res.reshape(img_np.shape)

        quantized_pil = Image.fromarray(quantized_img).convert("RGBA")
        w, h = quantized_pil.size

        # 1. 生成小像素画
        small_w = w // pixel_size
        small_h = h // pixel_size
        self.final_pixel_img = quantized_pil.resize((small_w, small_h), Image.NEAREST)

        # 2. 把小像素画 放大回【原图真实尺寸】（保持比例）
        self.preview_img = self.final_pixel_img.resize((self.original_w, self.original_h), Image.NEAREST)

        # 3. 预览展示：等比例缩到400画布内，不会超大溢出
        show_img = self.preview_img.copy()
        show_img.thumbnail((400, 400))
        self.tk_img_preview = ImageTk.PhotoImage(show_img)
        self.canvas_preview.delete("all")
        self.canvas_preview.create_image(200, 200, image=self.tk_img_preview)
        self.log(f"✅ 生成小像素：{small_w}×{small_h}，已放大回原图尺寸")

    def auto_cut_person(self):
        if self.preview_img is None:
            self.log("❌ 请先生成像素画")
            return
        img = np.array(self.preview_img.convert("RGB"))
        img_cv = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        h, w = img_cv.shape[:2]
        mask = np.zeros((h, w), np.uint8)
        rect = (5, 5, w - 10, h - 10)
        bgd = np.zeros((1, 65), np.float64)
        fgd = np.zeros((1, 65), np.float64)
        cv2.grabCut(img_cv, mask, rect, bgd, fgd, 5, cv2.GC_INIT_WITH_RECT)
        mask2 = np.where((mask == 2) | (mask == 0), 0, 255).astype(np.uint8)
        b, g, r = cv2.split(img_cv)
        rgba = cv2.merge((r, g, b, mask2))
        self.preview_img = Image.fromarray(rgba, "RGBA")

        # 编辑后依然适配400画布
        show_img = self.preview_img.copy()
        show_img.thumbnail((400, 400))
        self.tk_img_preview = ImageTk.PhotoImage(show_img)
        self.canvas_preview.delete("all")
        self.canvas_preview.create_image(200, 200, image=self.tk_img_preview)
        self.log("✅ 背景已透明")

    def add_white_border(self):
        if self.preview_img is None:
            self.log("❌ 请先生成像素画")
            return
        b = 10
        w, h = self.preview_img.size
        new_img = Image.new("RGBA", (w + b * 2, h + b * 2), (255, 255, 255, 255))
        new_img.paste(self.preview_img, (b, b), self.preview_img)
        self.preview_img = new_img

        show_img = self.preview_img.copy()
        show_img.thumbnail((400, 400))
        self.tk_img_preview = ImageTk.PhotoImage(show_img)
        self.canvas_preview.delete("all")
        self.canvas_preview.create_image(200, 200, image=self.tk_img_preview)
        self.log("✅ 已添加白色描边")

    def to_gray(self):
        if self.preview_img is None:
            self.log("❌ 请先生成像素画")
            return
        gray = self.preview_img.convert("L").convert("RGBA")
        self.preview_img = gray

        show_img = self.preview_img.copy()
        show_img.thumbnail((400, 400))
        self.tk_img_preview = ImageTk.PhotoImage(show_img)
        self.canvas_preview.delete("all")
        self.canvas_preview.create_image(200, 200, image=self.tk_img_preview)
        self.log("✅ 已转为灰度图像")

    def save_image(self):
        if self.preview_img is None:
            self.log("❌ 请先生成")
            return
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if path:
            self.preview_img.save(path)
            self.log("💾 保存成功！")


if __name__ == "__main__":
    root = tk.Tk()
    app = PixelArtApp(root)
    root.mainloop()