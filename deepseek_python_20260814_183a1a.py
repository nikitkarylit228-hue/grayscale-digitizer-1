import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import os

class GrayscaleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grayscale Digitizer")
        self.root.geometry("1100x750")
        self.root.configure(bg="#1a1a1a")
        self.image = None
        self.matrix = None
        self.levels = 10
        self.setup_ui()

    def setup_ui(self):
        top = tk.Frame(self.root, bg="#1a1a1a")
        top.pack(fill=tk.X, padx=10, pady=10)
        btn_style = {"bg": "#2a2a2a", "fg": "white", "font": ("Segoe UI", 11), "padx": 15, "pady": 8}
        tk.Button(top, text="📁 Загрузить фото", command=self.load_image, **btn_style).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="💾 Сохранить матрицу", command=self.save_matrix, **btn_style).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="📋 Копировать", command=self.copy_matrix, **btn_style).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="✕ Очистить", command=self.clear, bg="#442222", fg="white", font=("Segoe UI", 11), padx=15, pady=8).pack(side=tk.LEFT, padx=5)
        level_frame = tk.Frame(top, bg="#1a1a1a")
        level_frame.pack(side=tk.RIGHT)
        tk.Label(level_frame, text="Уровни (2-20):", bg="#1a1a1a", fg="#888", font=("Segoe UI", 11)).pack(side=tk.LEFT)
        self.level_var = tk.StringVar(value="10")
        self.spin = tk.Spinbox(level_frame, from_=2, to=20, width=4, textvariable=self.level_var, bg="#2a2a2a", fg="white", font=("Segoe UI", 12))
        self.spin.pack(side=tk.LEFT, padx=5)
        tk.Button(level_frame, text="Применить", command=self.apply_levels, bg="#003322", fg="white", font=("Segoe UI", 10), padx=12, pady=5).pack(side=tk.LEFT)
        main = tk.Frame(self.root, bg="#1a1a1a")
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        left = tk.Frame(main, bg="#0d0d0d", relief=tk.GROOVE, bd=2)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.preview = tk.Label(left, text="Загрузите изображение", bg="#0d0d0d", fg="#555", font=("Segoe UI", 16))
        self.preview.pack(pady=20)
        self.canvas = tk.Canvas(left, bg="#0d0d0d", highlightthickness=1, highlightbackground="#333")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        info = tk.Frame(left, bg="#0d0d0d")
        info.pack(fill=tk.X, padx=10, pady=5)
        self.size_label = tk.Label(info, text="0 x 0", bg="#0d0d0d", fg="#888", font=("Segoe UI", 10))
        self.size_label.pack(side=tk.LEFT, padx=5)
        self.pixels_label = tk.Label(info, text="0 пикселей", bg="#0d0d0d", fg="#888", font=("Segoe UI", 10))
        self.pixels_label.pack(side=tk.LEFT, padx=5)
        right = tk.Frame(main, bg="#0d0d0d", relief=tk.GROOVE, bd=2)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        tk.Label(right, text="МАТРИЦА ОТТЕНКОВ (0-9)", bg="#0d0d0d", fg="#00ff88", font=("Segoe UI", 13, "bold")).pack(pady=10)
        self.matrix_text = tk.Text(right, bg="#0a0a0a", fg="#00ff88", font=("Consolas", 9), wrap=tk.NONE)
        self.matrix_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.status = tk.Label(self.root, text="Готов к работе", bg="#1a1a1a", fg="#666", font=("Segoe UI", 10), anchor="w")
        self.status.pack(fill=tk.X, padx=10, pady=5)

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp")])
        if not path:
            return
        try:
            self.status.config(text="Обработка...")
            img = Image.open(path).convert("L")
            self.image = img
            arr = np.array(img, dtype=np.float32)
            step = 255 / (self.levels - 1)
            quantized = np.round(arr / step).astype(np.int32)
            quantized = np.clip(quantized, 0, self.levels - 1)
            self.matrix = quantized
            self.show_preview()
            self.show_matrix()
            self.draw_grid()
            w, h = img.width, img.height
            self.size_label.config(text=f"{w} x {h}")
            self.pixels_label.config(text=f"{w*h:,} пикселей")
            self.status.config(text=f"✅ Загружено: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.status.config(text="❌ Ошибка")

    def show_preview(self):
        preview = self.image.copy()
        preview.thumbnail((300, 300))
        imgtk = ImageTk.PhotoImage(preview)
        self.preview.config(image=imgtk)
        self.preview.image = imgtk

    def show_matrix(self):
        h, w = self.matrix.shape
        display_h = min(h, 50)
        display_w = min(w, 50)
        lines = []
        for y in range(display_h):
            lines.append(" ".join(f"{self.matrix[y][x]:2d}" for x in range(display_w)))
        output = "\n".join(lines)
        if h > 50 or w > 50:
            output += f"\n\n... и ещё {h-50} строк, {w-50} столбцов"
        self.matrix_text.delete("1.0", tk.END)
        self.matrix_text.insert("1.0", output)

    def draw_grid(self):
        h, w = self.matrix.shape
        max_show = 50
        show_h = min(h, max_show)
        show_w = min(w, max_show)
        canvas_w = self.canvas.winfo_width() if self.canvas.winfo_width() > 100 else 500
        canvas_h = self.canvas.winfo_height() if self.canvas.winfo_height() > 100 else 400
        cell_w = canvas_w // show_w
        cell_h = canvas_h // show_h
        cell_size = min(cell_w, cell_h, 25)
        if cell_size < 2:
            cell_size = 2
        self.canvas.config(width=cell_size * show_w, height=cell_size * show_h)
        self.canvas.delete("all")
        palette = [f"#{i*255//(self.levels-1):02x}{i*255//(self.levels-1):02x}{i*255//(self.levels-1):02x}" for i in range(self.levels)]
        for y in range(show_h):
            for x in range(show_w):
                val = self.matrix[y][x]
                x0, y0 = x * cell_size, y * cell_size
                self.canvas.create_rectangle(x0, y0, x0 + cell_size, y0 + cell_size, fill=palette[val], outline="#222")
                if cell_size >= 12:
                    color = "white" if val < 5 else "black"
                    font_size = max(8, int(cell_size * 0.5))
                    self.canvas.create_text(x0 + cell_size // 2, y0 + cell_size // 2, text=str(val), fill=color, font=("Arial", font_size, "bold"))

    def apply_levels(self):
        try:
            new_levels = int(self.level_var.get())
            if 2 <= new_levels <= 20:
                self.levels = new_levels
                if self.image is not None:
                    self.load_image()
            else:
                messagebox.showwarning("Ошибка", "Уровни от 2 до 20")
        except ValueError:
            pass

    def save_matrix(self):
        if self.matrix is None:
            messagebox.showwarning("Нет данных", "Сначала загрузите фото")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if path:
            with open(path, "w") as f:
                for row in self.matrix:
                    f.write(" ".join(map(str, row)) + "\n")
            self.status.config(text=f"✅ Сохранено: {os.path.basename(path)}")

    def copy_matrix(self):
        if self.matrix is None:
            messagebox.showwarning("Нет данных", "Сначала загрузите фото")
            return
        text = "\n".join(" ".join(map(str, row)) for row in self.matrix)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status.config(text="✅ Матрица скопирована")

    def clear(self):
        self.image = None
        self.matrix = None
        self.preview.config(image="", text="Загрузите фото")
        self.canvas.delete("all")
        self.matrix_text.delete("1.0", tk.END)
        self.size_label.config(text="0 x 0")
        self.pixels_label.config(text="0 пикселей")
        self.status.config(text="🧹 Очищено")

if __name__ == "__main__":
    root = tk.Tk()
    app = GrayscaleApp(root)
    root.mainloop()