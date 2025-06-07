import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.font import Font
from PIL import Image, ImageTk, ImageEnhance
import os

class ModernImageConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Foto Dönüştürücü")
        self.root.geometry("1050x700")
        self.root.configure(bg="#181A20")

        # Renkler
        self.colors = {
            'bg': '#181A20',
            'panel': '#23242B',
            'accent': '#5B8DEF',
            'accent_selected': '#3A6ED8',
            'button': '#23242B',
            'button_active': '#5B8DEF',
            'button_text': '#fff',
            'label': '#B0B3B8',
            'text': '#fff',
            'progress': '#5B8DEF',
            'slider': '#5B8DEF',
            'slider_bg': '#23242B',
            'danger': '#E94560',
        }

        self.title_font = Font(family="Segoe UI", size=13, weight="bold")
        self.menu_font = Font(family="Segoe UI", size=12, weight="bold")
        self.label_font = Font(family="Segoe UI", size=11)
        self.button_font = Font(family="Segoe UI", size=12, weight="bold")
        self.entry_font = Font(family="Segoe UI", size=12)

        self.selected_file = None
        self.original_image = None
        self.preview_image = None
        self.output_format = tk.StringVar(value="PNG")
        self.quality = tk.IntVar(value=90)
        self.progress_value = tk.IntVar(value=0)
        self.brightness = tk.DoubleVar(value=1.0)
        self.contrast = tk.DoubleVar(value=1.0)
        self.sharpness = tk.DoubleVar(value=1.0)
        self.rotate = tk.IntVar(value=0)
        self.width = tk.StringVar()
        self.height = tk.StringVar()
        self.filename_var = tk.StringVar()
        self._reset_state = {}

        self.setup_layout()

    def setup_layout(self):
        # Sol Menü
        self.menu_frame = tk.Frame(self.root, bg=self.colors['panel'], width=240)
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.menu_frame.pack_propagate(False)

        # Logo ve başlık
        logo_frame = tk.Frame(self.menu_frame, bg=self.colors['panel'])
        logo_frame.pack(pady=18, padx=8, anchor='w')
        tk.Label(logo_frame, text="🖼️", font=("Segoe UI", 18), bg=self.colors['panel'], fg=self.colors['accent']).pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(logo_frame, text="Foto Dönüştürücü", bg=self.colors['panel'], fg=self.colors['text'], font=self.title_font, anchor='w').pack(side=tk.LEFT)

        # Menü butonları
        self.menu_button("Upload", "📤", self.upload_file).pack(fill=tk.X, pady=5, padx=20)

        # Orta Ana Panel
        self.center_frame = tk.Frame(self.root, bg=self.colors['bg'])
        self.center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Preview başlık
        tk.Label(self.center_frame, text="Selects", bg=self.colors['bg'], fg=self.colors['label'], font=self.menu_font).pack(anchor='w')

        # Preview alanı
        self.preview_panel = tk.Frame(self.center_frame, bg=self.colors['panel'], width=400, height=250, bd=0, relief=tk.RIDGE)
        self.preview_panel.pack(pady=10)
        self.preview_panel.pack_propagate(False)
        self.preview_label = tk.Label(self.preview_panel, bg=self.colors['panel'])
        self.preview_label.pack(expand=True)
        self.update_preview()

        # Dosya adı değiştirme alanı
        filename_frame = tk.Frame(self.center_frame, bg=self.colors['bg'])
        filename_frame.pack(pady=5, anchor='w')
        tk.Label(filename_frame, text="Dosya Adı:", bg=self.colors['bg'], fg=self.colors['label'], font=self.label_font).pack(side=tk.LEFT, padx=5)
        self.filename_entry = tk.Entry(filename_frame, textvariable=self.filename_var, font=self.entry_font, width=30)
        self.filename_entry.pack(side=tk.LEFT, padx=5)

        # Format seçimi (alt alta, özel renk)
        format_frame = tk.Frame(self.center_frame, bg=self.colors['bg'])
        format_frame.pack(pady=10)
        self.format_buttons = {}
        for fmt in ["JPEG", "PNG", "TIFF", "WebP"]:
            btn = tk.Button(format_frame, text=fmt, width=16, font=self.button_font,
                             bg=self.colors['button'], fg="#fff", relief=tk.FLAT, bd=0,
                             activebackground=self.colors['button_active'], activeforeground="#fff",
                             cursor="hand2", command=lambda f=fmt: self.set_format(f))
            btn.pack(side=tk.TOP, pady=3, anchor='w')
            self.format_buttons[fmt] = btn
        self.update_format_colors()
        self.output_format.trace_add('write', lambda *a: self.update_format_colors())

        # Quality slider
        tk.Label(self.center_frame, text="Quality", bg=self.colors['bg'], fg=self.colors['label'], font=self.label_font).pack(anchor='w', pady=(20, 0))
        self.quality_slider = ttk.Scale(self.center_frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.quality, command=self.update_quality_label)
        self.quality_slider.set(90)
        self.quality_slider.pack(fill=tk.X, pady=5)
        self.quality_label = tk.Label(self.center_frame, text="90%", bg=self.colors['bg'], fg=self.colors['accent'], font=self.label_font)
        self.quality_label.pack(anchor='e')

        # Dönüştür ve Reset butonları
        btn_frame = tk.Frame(self.center_frame, bg=self.colors['bg'])
        btn_frame.pack(pady=20)
        self.convert_button = tk.Button(btn_frame, text="Convert", bg=self.colors['accent'], fg="#fff", font=self.button_font, relief=tk.FLAT, padx=20, pady=10, command=self.convert_image, cursor="hand2")
        self.convert_button.pack(side=tk.LEFT, padx=10)
        self.reset_button = tk.Button(btn_frame, text="Reset", bg=self.colors['danger'], fg="#fff", font=self.button_font, relief=tk.FLAT, padx=20, pady=10, command=self.reset_all, cursor="hand2")
        self.reset_button.pack(side=tk.LEFT, padx=10)

        # Progress bar
        progress_frame = tk.Frame(self.center_frame, bg=self.colors['bg'])
        progress_frame.pack(fill=tk.X, pady=20)
        tk.Label(progress_frame, text="Progress", bg=self.colors['bg'], fg=self.colors['label'], font=self.label_font).pack(anchor='w')
        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", length=300, mode="determinate", variable=self.progress_value)
        self.progress.pack(fill=tk.X, pady=5)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar", foreground=self.colors['progress'], background=self.colors['progress'], troughcolor=self.colors['slider_bg'], bordercolor=self.colors['slider_bg'], lightcolor=self.colors['progress'], darkcolor=self.colors['progress'])

        # Sağ Panel
        self.right_frame = tk.Frame(self.root, bg=self.colors['panel'], width=320)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=0, pady=0)
        self.right_frame.pack_propagate(False)

        tk.Label(self.right_frame, text="Adjustments", bg=self.colors['panel'], fg=self.colors['text'], font=self.menu_font, pady=15).pack(anchor='w', padx=20)
        adj_frame = tk.LabelFrame(self.right_frame, text="Apply adjustment", bg=self.colors['panel'], fg=self.colors['label'], font=self.label_font, bd=1, relief=tk.GROOVE, labelanchor='n')
        adj_frame.pack(fill=tk.X, padx=20, pady=10)
        # Parlaklık
        tk.Label(adj_frame, text="Brightness", bg=self.colors['panel'], fg=self.colors['label'], font=self.label_font).pack(anchor='w', pady=2)
        self.brightness_slider = ttk.Scale(adj_frame, from_=0.5, to=2.0, orient=tk.HORIZONTAL, variable=self.brightness, command=lambda e: self.update_preview())
        self.brightness_slider.pack(fill=tk.X, pady=2)
        # Kontrast
        tk.Label(adj_frame, text="Contrast", bg=self.colors['panel'], fg=self.colors['label'], font=self.label_font).pack(anchor='w', pady=2)
        self.contrast_slider = ttk.Scale(adj_frame, from_=0.5, to=2.0, orient=tk.HORIZONTAL, variable=self.contrast, command=lambda e: self.update_preview())
        self.contrast_slider.pack(fill=tk.X, pady=2)
        # Keskinlik
        tk.Label(adj_frame, text="Sharpness", bg=self.colors['panel'], fg=self.colors['label'], font=self.label_font).pack(anchor='w', pady=2)
        self.sharpness_slider = ttk.Scale(adj_frame, from_=0.5, to=2.0, orient=tk.HORIZONTAL, variable=self.sharpness, command=lambda e: self.update_preview())
        self.sharpness_slider.pack(fill=tk.X, pady=2)
        # Döndürme
        tk.Label(adj_frame, text="Rotate", bg=self.colors['panel'], fg=self.colors['label'], font=self.label_font).pack(anchor='w', pady=2)
        rotate_frame = tk.Frame(adj_frame, bg=self.colors['panel'])
        rotate_frame.pack(fill=tk.X, pady=2)
        self.rotate_slider = ttk.Scale(rotate_frame, from_=0, to=359, orient=tk.HORIZONTAL, variable=self.rotate, command=lambda e: self.update_preview())
        self.rotate_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.rotate_label = tk.Label(rotate_frame, text="0°", bg=self.colors['panel'], fg=self.colors['label'], font=self.label_font)
        self.rotate_label.pack(side=tk.LEFT, padx=5)
        self.rotate.trace_add('write', self.update_rotate_label)
        # Boyutlandırma
        size_frame = tk.LabelFrame(self.right_frame, text="Resize", bg=self.colors['panel'], fg=self.colors['label'], font=self.label_font, bd=1, relief=tk.GROOVE, labelanchor='n')
        size_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(size_frame, text="Width:", bg=self.colors['panel'], fg=self.colors['label'], font=self.label_font).pack(side=tk.LEFT, padx=5)
        self.width_entry = tk.Entry(size_frame, textvariable=self.width, width=6, font=self.entry_font)
        self.width_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(size_frame, text="Height:", bg=self.colors['panel'], fg=self.colors['label'], font=self.label_font).pack(side=tk.LEFT, padx=5)
        self.height_entry = tk.Entry(size_frame, textvariable=self.height, width=6, font=self.entry_font)
        self.height_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(size_frame, text="Apply", bg=self.colors['accent'], fg="#fff", font=self.button_font, relief=tk.FLAT, command=self.apply_resize, cursor="hand2").pack(side=tk.LEFT, padx=10)

    def menu_button(self, text, icon, command):
        btn = tk.Button(self.menu_frame, text=f"{icon}  {text}", bg=self.colors['button'], fg=self.colors['button_text'], font=self.menu_font, relief=tk.FLAT, padx=10, pady=8, anchor='w', activebackground=self.colors['button_active'], activeforeground=self.colors['button_text'], command=command)
        btn.configure(cursor="hand2")
        return btn

    def set_format(self, fmt):
        self.output_format.set(fmt)
        self.update_format_colors()
        self.update_preview()

    def update_format_colors(self, *args):
        for fmt, btn in self.format_buttons.items():
            if self.output_format.get() == fmt:
                btn.config(bg=self.colors['accent_selected'])
            else:
                btn.config(bg=self.colors['button'])

    def upload_file(self):
        filetypes = [("Image files", "*.jpg *.jpeg *.png *.bmp *.webp *.tiff")]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.selected_file = filename
            self.original_image = Image.open(filename)
            self.width.set(str(self.original_image.width))
            self.height.set(str(self.original_image.height))
            # Dosya adı otomatik olarak önerilsin
            base = os.path.splitext(os.path.basename(filename))[0]
            self.filename_var.set(base)
            # Reset için ilk halini kaydet
            self._reset_state = {
                'output_format': self.output_format.get(),
                'quality': self.quality.get(),
                'brightness': self.brightness.get(),
                'contrast': self.contrast.get(),
                'sharpness': self.sharpness.get(),
                'rotate': self.rotate.get(),
                'width': self.width.get(),
                'height': self.height.get(),
                'filename': self.filename_var.get(),
            }
            self.update_preview()

    def reset_all(self):
        if not self.original_image or not self._reset_state:
            return
        self.output_format.set(self._reset_state['output_format'])
        self.quality.set(self._reset_state['quality'])
        self.brightness.set(self._reset_state['brightness'])
        self.contrast.set(self._reset_state['contrast'])
        self.sharpness.set(self._reset_state['sharpness'])
        self.rotate.set(self._reset_state['rotate'])
        self.width.set(self._reset_state['width'])
        self.height.set(self._reset_state['height'])
        self.filename_var.set(self._reset_state['filename'])
        self.update_format_colors()
        self.update_preview()

    def update_preview(self, *args):
        if self.original_image:
            img = self.original_image.copy()
            # Boyutlandırma sadece önizlemede uygula
            try:
                w = int(self.width.get()) if self.width.get() else img.width
                h = int(self.height.get()) if self.height.get() else img.height
                if w > 0 and h > 0:
                    img = img.resize((w, h), Image.LANCZOS)
            except Exception:
                pass  # Geçersiz değer girilirse orijinal boyutla devam et
            # Uygula: parlaklık, kontrast, keskinlik, döndürme
            img = ImageEnhance.Brightness(img).enhance(self.brightness.get())
            img = ImageEnhance.Contrast(img).enhance(self.contrast.get())
            img = ImageEnhance.Sharpness(img).enhance(self.sharpness.get())
            if self.rotate.get() != 0:
                img = img.rotate(-self.rotate.get(), expand=True)
            img.thumbnail((380, 220))
            self.preview_image = ImageTk.PhotoImage(img)
            self.preview_label.config(image=self.preview_image)
        else:
            self.preview_label.config(image='', text='No Image', fg=self.colors['label'], font=self.label_font)

    def update_quality_label(self, val=None):
        self.quality_label.config(text=f"{int(float(self.quality.get()))}%")
        self.update_preview()

    def update_rotate_label(self, *args):
        self.rotate_label.config(text=f"{int(self.rotate.get())}°")

    def apply_resize(self):
        if not self.original_image:
            return
        try:
            w = int(self.width.get()) if self.width.get() else self.original_image.width
            h = int(self.height.get()) if self.height.get() else self.original_image.height
            if w > 0 and h > 0:
                self.width.set(str(w))
                self.height.set(str(h))
                # Sadece önizlemeyi güncelle, orijinali değiştirme
                self.update_preview()
            else:
                messagebox.showerror("Error", "Invalid width or height!")
        except Exception:
            messagebox.showerror("Error", "Invalid width or height!")

    def convert_image(self):
        if not self.selected_file or not self.original_image:
            messagebox.showerror("Error", "Please upload an image first.")
            return
        out_format = self.output_format.get().lower()
        out_ext = {
            'jpeg': '.jpg',
            'png': '.png',
            'tiff': '.tiff',
            'webp': '.webp',
        }[out_format]
        # Dosya adı
        new_name = self.filename_var.get().strip()
        if not new_name:
            messagebox.showerror("Error", "Please enter a file name!")
            return
        out_dir = os.path.dirname(self.selected_file)
        out_file = os.path.join(out_dir, new_name + '_converted' + out_ext)
        img = self.original_image.copy()
        # Boyutlandırma uygula
        try:
            w = int(self.width.get()) if self.width.get() else img.width
            h = int(self.height.get()) if self.height.get() else img.height
            if w > 0 and h > 0:
                img = img.resize((w, h), Image.LANCZOS)
            else:
                messagebox.showerror("Error", "Invalid width or height!")
                return
        except Exception:
            messagebox.showerror("Error", "Invalid width or height!")
            return
        # Uygula: parlaklık, kontrast, keskinlik, döndürme
        img = ImageEnhance.Brightness(img).enhance(self.brightness.get())
        img = ImageEnhance.Contrast(img).enhance(self.contrast.get())
        img = ImageEnhance.Sharpness(img).enhance(self.sharpness.get())
        if self.rotate.get() != 0:
            img = img.rotate(-self.rotate.get(), expand=True)
        # Kalite
        quality = int(self.quality.get())
        self.progress_value.set(0)
        self.root.update()
        try:
            if out_format == 'jpeg':
                img = img.convert('RGB')
                img.save(out_file, quality=quality)
            else:
                img.save(out_file, quality=quality)
            self.progress_value.set(100)
            messagebox.showinfo("Success", f"Image converted and saved as:\n{out_file}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        self.progress_value.set(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernImageConverter(root)
    root.mainloop() 