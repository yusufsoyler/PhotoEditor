import os
from PIL import Image, ImageEnhance, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Scale
from tkinter.font import Font

class ImageConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Gelişmiş Resim İşleme Aracı")
        self.root.geometry("1200x800")
        
        # Modern ve yumuşak renk paleti
        self.colors = {
            'bg': '#f6f8fc',           # Çok açık mavi-gri arka plan
            'panel': '#e3e7f1',       # Hafif morumsu panel
            'button': '#5b8def',      # Modern mavi buton
            'button_hover': '#3a6ed8',# Koyu mavi hover
            'button_text': '#ffffff', # Beyaz buton yazısı
            'text': '#22223b',        # Koyu mor-mavi metin
            'label': '#4a4e69',       # Açık koyu metin
            'entry': '#ffffff',       # Beyaz giriş alanı
            'entry_border': '#bfc9da',# Gri-mavi kenarlık
            'frame': '#dbeafe',       # Açık mavi panel
            'highlight': '#a5b4fc',   # Hafif mor-mavi vurgu
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Fontlar
        self.title_font = Font(family="Segoe UI", size=22, weight="bold")
        self.button_font = Font(family="Segoe UI", size=13, weight="bold")
        self.label_font = Font(family="Segoe UI", size=11)
        self.entry_font = Font(family="Segoe UI", size=12)
        
        # Ana başlık
        title_frame = tk.Frame(root, bg=self.colors['bg'], pady=20)
        title_frame.pack(fill=tk.X)
        
        title = tk.Label(title_frame, text="Gelişmiş Resim İşleme Aracı", 
                        font=self.title_font, bg=self.colors['bg'],
                        fg=self.colors['text'])
        title.pack()

        # Ana frame'ler
        self.left_frame = tk.Frame(root, bg=self.colors['bg'])
        self.left_frame.pack(side=tk.LEFT, padx=30, pady=20, fill=tk.BOTH, expand=True)
        
        self.right_frame = tk.Frame(root, bg=self.colors['bg'])
        self.right_frame.pack(side=tk.RIGHT, padx=30, pady=20, fill=tk.BOTH, expand=True)

        # Sol frame içeriği
        self.setup_left_frame()
        
        # Sağ frame içeriği
        self.setup_right_frame()

        self.selected_file = None
        self.original_image = None
        self.current_image = None
        self.preview_image = None
        self.crop_start = None
        self.crop_end = None
        self.history = []

    def create_button(self, parent, text, command, state=tk.NORMAL):
        button = tk.Button(parent, text=text, command=command,
                         bg=self.colors['button'], fg=self.colors['button_text'],
                         font=self.button_font, padx=20, pady=10,
                         state=state, relief=tk.FLAT, bd=0,
                         activebackground=self.colors['button_hover'],
                         activeforeground=self.colors['button_text'],
                         highlightthickness=0)
        button.configure(cursor="hand2")
        button.bind("<Enter>", lambda e: button.config(bg=self.colors['button_hover']))
        button.bind("<Leave>", lambda e: button.config(bg=self.colors['button']))
        button.configure(borderwidth=0, highlightbackground=self.colors['highlight'])
        return button

    def setup_left_frame(self):
        # Dosya seçme butonu
        self.select_button = self.create_button(self.left_frame, "Dosya Seç", self.select_file)
        self.select_button.pack(pady=10)

        # Dosya adı düzenleme alanı
        filename_frame = tk.Frame(self.left_frame, bg=self.colors['bg'])
        filename_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(filename_frame, text="Dosya Adı:", 
                bg=self.colors['bg'], font=self.label_font,
                fg=self.colors['label']).pack(side=tk.LEFT, padx=5)
        
        self.filename_var = tk.StringVar()
        self.filename_entry = tk.Entry(filename_frame, textvariable=self.filename_var,
                                     font=self.entry_font, bg=self.colors['entry'],
                                     fg=self.colors['text'], width=30,
                                     relief=tk.FLAT, highlightthickness=1,
                                     highlightbackground=self.colors['entry_border'],
                                     highlightcolor=self.colors['highlight'])
        self.filename_entry.pack(side=tk.LEFT, padx=5)
        self.filename_entry.config(state=tk.DISABLED)

        # Önizleme alanı
        self.preview_frame = tk.Frame(self.left_frame, bg=self.colors['frame'],
                               bd=0, relief=tk.RIDGE, highlightbackground=self.colors['highlight'], highlightthickness=2)
        self.preview_frame.pack(pady=15, fill=tk.BOTH, expand=True)
        
        self.preview_label = tk.Label(self.preview_frame, bg=self.colors['frame'])
        self.preview_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Format seçme alanı
        format_frame = tk.Frame(self.left_frame, bg=self.colors['bg'])
        format_frame.pack(pady=20)

        tk.Label(format_frame, text="Hedef Format:", 
                bg=self.colors['bg'], font=self.label_font,
                fg=self.colors['label']).pack(side=tk.LEFT, padx=5)
        
        self.format_var = tk.StringVar(value='.png')
        self.format_combo = ttk.Combobox(format_frame, 
                                       textvariable=self.format_var,
                                       values=['.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff'],
                                       state="readonly",
                                       width=10)
        self.format_combo.pack(side=tk.LEFT, padx=5)

        # Butonlar frame
        buttons_frame = tk.Frame(self.left_frame, bg=self.colors['bg'])
        buttons_frame.pack(pady=20)

        self.convert_button = self.create_button(buttons_frame, "Dönüştür ve Kaydet",
                                               self.convert_image, state=tk.DISABLED)
        self.convert_button.pack(side=tk.LEFT, padx=10)

        self.reset_button = self.create_button(buttons_frame, "Değişiklikleri Geri Al",
                                             self.reset_image, state=tk.DISABLED)
        self.reset_button.pack(side=tk.LEFT, padx=10)

    def setup_right_frame(self):
        options_frame = tk.LabelFrame(self.right_frame, text="Resim İşleme Seçenekleri",
                                    bg=self.colors['panel'], font=self.label_font,
                                    fg=self.colors['label'], bd=2, relief=tk.GROOVE, labelanchor='n')
        options_frame.pack(fill=tk.X, pady=10)

        # Boyutlandırma
        size_frame = tk.Frame(options_frame, bg=self.colors['panel'])
        size_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(size_frame, text="Genişlik:", 
                bg=self.colors['panel'], font=self.label_font,
                fg=self.colors['label']).pack(side=tk.LEFT, padx=5)
        
        self.width_var = tk.StringVar()
        self.width_entry = tk.Entry(size_frame, textvariable=self.width_var,
                                  font=self.entry_font, bg=self.colors['entry'],
                                  fg=self.colors['text'], width=8,
                                  relief=tk.FLAT, highlightthickness=1,
                                  highlightbackground=self.colors['entry_border'],
                                  highlightcolor=self.colors['highlight'])
        self.width_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(size_frame, text="Yükseklik:", 
                bg=self.colors['panel'], font=self.label_font,
                fg=self.colors['label']).pack(side=tk.LEFT, padx=5)
        
        self.height_var = tk.StringVar()
        self.height_entry = tk.Entry(size_frame, textvariable=self.height_var,
                                   font=self.entry_font, bg=self.colors['entry'],
                                   fg=self.colors['text'], width=8,
                                   relief=tk.FLAT, highlightthickness=1,
                                   highlightbackground=self.colors['entry_border'],
                                   highlightcolor=self.colors['highlight'])
        self.height_entry.pack(side=tk.LEFT, padx=5)
        
        self.resize_button = self.create_button(size_frame, "Boyutlandır",
                                              self.resize_image, state=tk.DISABLED)
        self.resize_button.pack(side=tk.LEFT, padx=5)

        # Döndürme
        rotate_frame = tk.Frame(options_frame, bg=self.colors['panel'])
        rotate_frame.pack(fill=tk.X, pady=5)
        
        self.rotate_var = tk.IntVar(value=0)
        self.rotate_scale = Scale(rotate_frame, from_=0, to=360, orient=tk.HORIZONTAL,
                                variable=self.rotate_var, label="Döndürme Açısı",
                                bg=self.colors['panel'], fg=self.colors['label'],
                                troughcolor=self.colors['highlight'],
                                highlightthickness=0, bd=0, font=self.label_font)
        self.rotate_scale.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.rotate_button = self.create_button(rotate_frame, "Döndür",
                                              self.rotate_image, state=tk.DISABLED)
        self.rotate_button.pack(side=tk.LEFT, padx=5)

        # Renk ayarları
        color_frame = tk.LabelFrame(options_frame, text="Renk Ayarları",
                                  bg=self.colors['panel'], font=self.label_font,
                                  fg=self.colors['label'], bd=1, relief=tk.GROOVE, labelanchor='n')
        color_frame.pack(fill=tk.X, pady=5)

        self.brightness_var = tk.DoubleVar(value=1.0)
        tk.Label(color_frame, text="Parlaklık:", 
                bg=self.colors['panel'], font=self.label_font,
                fg=self.colors['label']).pack()
        
        self.brightness_scale = Scale(color_frame, from_=0.0, to=2.0, resolution=0.1,
                                    variable=self.brightness_var, orient=tk.HORIZONTAL,
                                    bg=self.colors['panel'], fg=self.colors['label'],
                                    troughcolor=self.colors['highlight'],
                                    highlightthickness=0, bd=0, font=self.label_font)
        self.brightness_scale.pack(fill=tk.X, padx=5)
        
        self.contrast_var = tk.DoubleVar(value=1.0)
        tk.Label(color_frame, text="Kontrast:", 
                bg=self.colors['panel'], font=self.label_font,
                fg=self.colors['label']).pack()
        
        self.contrast_scale = Scale(color_frame, from_=0.0, to=2.0, resolution=0.1,
                                  variable=self.contrast_var, orient=tk.HORIZONTAL,
                                  bg=self.colors['panel'], fg=self.colors['label'],
                                  troughcolor=self.colors['highlight'],
                                  highlightthickness=0, bd=0, font=self.label_font)
        self.contrast_scale.pack(fill=tk.X, padx=5)
        
        self.sharpness_var = tk.DoubleVar(value=1.0)
        tk.Label(color_frame, text="Keskinlik:", 
                bg=self.colors['panel'], font=self.label_font,
                fg=self.colors['label']).pack()
        
        self.sharpness_scale = Scale(color_frame, from_=0.0, to=2.0, resolution=0.1,
                                   variable=self.sharpness_var, orient=tk.HORIZONTAL,
                                   bg=self.colors['panel'], fg=self.colors['label'],
                                   troughcolor=self.colors['highlight'],
                                   highlightthickness=0, bd=0, font=self.label_font)
        self.sharpness_scale.pack(fill=tk.X, padx=5)

        self.apply_color_button = self.create_button(color_frame, "Renk Ayarlarını Uygula",
                                                   self.apply_color_adjustments,
                                                   state=tk.DISABLED)
        self.apply_color_button.pack(pady=5)

    def save_state(self):
        """Mevcut durumu kaydet"""
        if self.current_image:
            self.history.append({
                'image': self.current_image.copy(),
                'brightness': self.brightness_var.get(),
                'contrast': self.contrast_var.get(),
                'sharpness': self.sharpness_var.get(),
                'rotate': self.rotate_var.get(),
                'width': self.width_var.get(),
                'height': self.height_var.get()
            })

    def update_preview(self):
        if self.current_image:
            preview_width = self.preview_frame.winfo_width()
            preview_height = self.preview_frame.winfo_height()

            # Eğer frame boyutları hazır değilse tekrar dene
            if preview_width <= 1 or preview_height <= 1:
                self.root.after(100, self.update_preview)
                return

            # Resmi önizleme alanına sığdır
            img_width, img_height = self.current_image.size
            ratio = min(preview_width/img_width, preview_height/img_height)
            new_size = (int(img_width * ratio), int(img_height * ratio))

            # Resmi yeniden boyutlandır
            preview_img = self.current_image.copy()
            preview_img.thumbnail(new_size, Image.Resampling.LANCZOS)

            # Tkinter için resmi dönüştür
            self.preview_image = ImageTk.PhotoImage(preview_img)
            self.preview_label.config(image=self.preview_image)
            self.preview_label.image = self.preview_image  # Referansı koru

    def select_file(self):
        filetypes = [("Image files", "*.jpg *.jpeg *.png *.bmp *.webp *.tiff")]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        
        if filename:
            self.selected_file = filename
            base_name = os.path.splitext(os.path.basename(filename))[0]
            self.filename_var.set(base_name)
            self.filename_entry.config(state=tk.NORMAL)
            
            self.convert_button.config(state=tk.NORMAL)
            self.resize_button.config(state=tk.NORMAL)
            self.rotate_button.config(state=tk.NORMAL)
            self.apply_color_button.config(state=tk.NORMAL)
            self.reset_button.config(state=tk.NORMAL)
            
            # Resmi yükle
            self.original_image = Image.open(filename)
            self.current_image = self.original_image.copy()
            
            # Boyut girişlerini güncelle
            self.width_var.set(str(self.original_image.width))
            self.height_var.set(str(self.original_image.height))
            
            # Geçmişi temizle
            self.history = []
            
            # Önizlemeyi güncelle
            self.root.update()
            self.update_preview()

    def resize_image(self):
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            if width > 0 and height > 0:
                self.save_state()  # Mevcut durumu kaydet
                self.current_image = self.current_image.resize((width, height), Image.Resampling.LANCZOS)
                self.update_preview()
                messagebox.showinfo("Başarılı", "Resim boyutlandırıldı!")
            else:
                messagebox.showerror("Hata", "Geçersiz boyut değerleri!")
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayısal değerler girin!")

    def rotate_image(self):
        angle = self.rotate_var.get()
        self.save_state()  # Mevcut durumu kaydet
        self.current_image = self.current_image.rotate(angle, expand=True)
        self.update_preview()
        messagebox.showinfo("Başarılı", f"Resim {angle} derece döndürüldü!")

    def apply_color_adjustments(self):
        if self.current_image:
            self.save_state()  # Mevcut durumu kaydet
            # Parlaklık ayarı
            brightness = ImageEnhance.Brightness(self.current_image)
            self.current_image = brightness.enhance(self.brightness_var.get())
            
            # Kontrast ayarı
            contrast = ImageEnhance.Contrast(self.current_image)
            self.current_image = contrast.enhance(self.contrast_var.get())
            
            # Keskinlik ayarı
            sharpness = ImageEnhance.Sharpness(self.current_image)
            self.current_image = sharpness.enhance(self.sharpness_var.get())
            
            self.update_preview()
            messagebox.showinfo("Başarılı", "Renk ayarları uygulandı!")

    def reset_image(self):
        if self.history:  # Eğer geçmiş varsa
            last_state = self.history.pop()  # Son durumu al
            self.current_image = last_state['image']
            self.brightness_var.set(last_state['brightness'])
            self.contrast_var.set(last_state['contrast'])
            self.sharpness_var.set(last_state['sharpness'])
            self.rotate_var.set(last_state['rotate'])
            self.width_var.set(last_state['width'])
            self.height_var.set(last_state['height'])
            self.update_preview()
            messagebox.showinfo("Başarılı", "Son değişiklik geri alındı!")
        elif self.original_image:  # Geçmiş yoksa orijinal resme dön
            self.current_image = self.original_image.copy()
            self.brightness_var.set(1.0)
            self.contrast_var.set(1.0)
            self.sharpness_var.set(1.0)
            self.rotate_var.set(0)
            self.width_var.set(str(self.original_image.width))
            self.height_var.set(str(self.original_image.height))
            self.update_preview()
            messagebox.showinfo("Başarılı", "Resim orijinal haline döndürüldü!")

    def convert_image(self):
        if not self.selected_file or not self.current_image:
            return

        try:
            # Dosya adını al
            new_filename = self.filename_var.get().strip()
            if not new_filename:
                messagebox.showerror("Hata", "Lütfen bir dosya adı girin!")
                return

            # Orijinal dosya yolunu al
            original_dir = os.path.dirname(self.selected_file)
            new_format = self.format_var.get()
            
            # Yeni dosya adını oluştur
            new_file = os.path.join(original_dir, f"{new_filename}{new_format}")
            
            # Resmi kaydet
            if new_format in ['.jpg', '.jpeg'] and self.current_image.mode in ['RGBA', 'LA']:
                background = Image.new('RGB', self.current_image.size, (255, 255, 255))
                background.paste(self.current_image, mask=self.current_image.split()[-1])
                background.save(new_file, quality=95)
            else:
                self.current_image.save(new_file)

            messagebox.showinfo("Başarılı", 
                              f"Dönüştürme tamamlandı!\nDosya kaydedildi: {new_file}")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Dönüştürme sırasında bir hata oluştu:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageConverter(root)
    root.mainloop() 