import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

# 我修改
# ---------------------- 主程序 ----------------------
class PixelArtApp:
    def __init__(self, root):
        self.root = root
        self.root.title("像素画生成器")
        self.root.geometry("1000x600")

        # 变量
        self.original_img = None
        self.cropped_img = None
        self.pixel_img = None
        self.pixel_size = 8

        # 左侧面板
        left_frame = ttk.Frame(root, width=480, height=550)
        left_frame.pack(side=tk.LEFT, padx=10, pady=10)
        left_frame.pack_propagate(False)

        # 右侧面板
        right_frame = ttk.Frame(root, width=480, height=550)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        right_frame.pack_propagate(False)

        # 原始图片
        ttk.Label(left_frame, text="原始图片", font=("黑体", 14)).pack(pady=5)
        self.canvas_original = tk.Canvas(left_frame, bg="white", width=400, height=400)
        self.canvas_original.pack()

        # 尺寸显示
        self.size_label = ttk.Label(left_frame, text="图片尺寸：未上传", font=("黑体", 11))
        self.size_label.pack(pady=3)

        # 像素化强度
        ttk.Label(left_frame, text="像素化强度（数字越大越明显）").pack()
        self.pixel_entry = ttk.Entry(left_frame, width=10)
        self.pixel_entry.insert(0, "8")
        self.pixel_entry.pack(pady=3)

        # 按钮
        ttk.Button(left_frame, text="选择图片", command=self.load_image).pack(pady=2)
        ttk.Button(left_frame, text="生成像素画", command=self.make_pixel_art).pack(pady=2)

        # 预览
        ttk.Label(right_frame, text="像素画预览", font=("黑体", 14)).pack(pady=5)
        self.canvas_result = tk.Canvas(right_frame, bg="white", width=400, height=400)
        self.canvas_result.pack()

        # 保存
        ttk.Button(right_frame, text="保存图片", command=self.save_image).pack(pady=10)

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("图片", "*.jpg *.jpeg *.png")])
        if not path:
            return

        img = Image.open(path).convert("RGB")
        self.original_img = img

        w, h = img.size
        self.size_label.config(text=f"图片尺寸：{w} × {h} px")

        # 自动裁剪正方形
        min_side = min(w, h)
        left = (w - min_side) // 2
        top = (h - min_side) // 2
        self.cropped_img = img.crop((left, top, left + min_side, top + min_side))

        self.show_img_on_canvas(self.cropped_img, self.canvas_original)

    def make_pixel_art(self):
        if self.cropped_img is None:
            messagebox.showwarning("提示", "请先上传图片")
            return

        try:
            size = int(self.pixel_entry.get())
            size = max(1, size)
        except:
            size = 8
        self.pixel_size = size

        img = self.cropped_img
        w, h = img.size
        small = img.resize((w // size, h // size), Image.NEAREST)
        result = small.resize((w, h), Image.NEAREST)

        self.pixel_img = result
        self.show_img_on_canvas(result, self.canvas_result)

    def show_img_on_canvas(self, img, canvas):
        img.thumbnail((400, 400))
        self.tk_img = ImageTk.PhotoImage(img)
        canvas.delete("all")
        canvas.create_image(200, 200, image=self.tk_img)

    def save_image(self):
        if self.pixel_img is None:
            messagebox.showwarning("提示", "先生成图片再保存")
            return
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if path:
            self.pixel_img.save(path)
            messagebox.showinfo("成功", "图片已保存！")

if __name__ == "__main__":
    root = tk.Tk()
    app = PixelArtApp(root)
    root.mainloop()