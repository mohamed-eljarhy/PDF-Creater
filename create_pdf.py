import os
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
import arabic_reshaper
from bidi.algorithm import get_display

# إعدادات المظهر
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# دالة معالجة النصوص العربية
def fix_ar(text):
    if not text: return ""
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

class MyMessageBox(ctk.CTkToplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.title(fix_ar(title))
        self.geometry("350x180")
        self.attributes("-topmost", True)
        self.label = ctk.CTkLabel(self, text=fix_ar(message), font=("Inter", 16))
        self.label.pack(expand=True, pady=25)
        self.btn = ctk.CTkButton(self, text=fix_ar("accept"), command=self.destroy, width=120, font=("Inter", 14, "bold"))
        self.btn.pack(pady=15)

class HousingPDFApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # --- التعديل الجوهري لحل مشكلة شريط العنوان ---
        self.overrideredirect(True) # إخفاء شريط عنوان الويندوز الأصلي
        
        self.geometry("600x550")
        self.file_paths = []
        
        # متغيرات سحب النافذة
        self._offsetx = 0
        self._offsety = 0

        # --- إنشاء شريط عنوان مخصص داخل التطبيق ---
        self.title_bar = ctk.CTkFrame(self, height=35, fg_color="#1a1a1a", corner_radius=0)
        self.title_bar.pack(fill="x")
        
        # زر الإغلاق المخصص
        self.close_btn = ctk.CTkButton(self.title_bar, text="✕", width=35, height=35, 
                                        fg_color="#1a1a1a", text_color="white",
                                        hover_color="#e74c3c", corner_radius=0, command=self.destroy)
        self.close_btn.pack(side="right")
        
        # زر التصغير المخصص (اختياري)
        self.min_btn = ctk.CTkButton(self.title_bar, text="—", width=35, height=35, 
                                       fg_color="#1a1a1a", text_color="white",
                                       hover_color="#555555", corner_radius=0, command=self.iconify)
        self.min_btn.pack(side="right")

        # العنوان في المنتصف (بخط Inter الاحترافي)
        self.title_label = ctk.CTkLabel(self.title_bar, text=fix_ar("pdf_maker"), 
                                         font=("Inter", 14))
        self.title_label.pack(side="left", padx=15)

        # ربط أحداث الفأرة لسحب النافذة
        self.title_bar.bind("<Button-1>", self.clickwin)
        self.title_bar.bind("<B1-Motion>", self.dragwin)
        self.title_label.bind("<Button-1>", self.clickwin)
        self.title_label.bind("<B1-Motion>", self.dragwin)

        # --- بقية عناصر الواجهة كما هي (مع تحسين الخطوط) ---
        font_title = ("Inter", 24, "bold")
        font_button = ("Inter", 16, "bold")
        font_text = ("Segoe UI", 14)
        font_status = ("Segoe UI", 14, "italic")

        # حاوية المحتوى الرئيسي (Main Container)
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=30, pady=20)

        # العنوان الرئيسي
        self.label = ctk.CTkLabel(self.main_container, text=fix_ar("embedded files in one pdf file"), 
                                  font=font_title)
        self.label.pack(pady=25)

        # زر اختيار الملفات
        self.btn_select = ctk.CTkButton(self.main_container, text=fix_ar("choose imgs&docs"), 
                                        command=self.select_files, font=font_button)
        self.btn_select.pack(pady=10)

        # صندوق عرض أسماء الملفات المختارة
        self.files_text = ctk.CTkTextbox(self.main_container, width=500, height=180, font=font_text)
        self.files_text.pack(pady=10)
        self.files_text.insert("0.0", fix_ar("لم يتم اختيار ملفات بعد..."))

        # زر التحويل والحفظ
        self.btn_convert = ctk.CTkButton(self.main_container, text=fix_ar("convert & save"), 
                                         command=self.convert_to_pdf, 
                                         fg_color="#27ae60", hover_color="#1e8449",
                                         font=font_button)
        self.btn_convert.pack(pady=20)

        # نص الحالة
        self.status_label = ctk.CTkLabel(self.main_container, text="", text_color="#f1c40f", font=font_status)
        self.status_label.pack(pady=5)

    # دوال سحب النافذة المخصصة
    def clickwin(self, event):
        self._offsetx = event.x
        self._offsety = event.y

    def dragwin(self, event):
        x = self.winfo_pointerx() - self._offsetx
        y = self.winfo_pointery() - self._offsety
        self.geometry(f"+{x}+{y}")

    # (بقية الدوال كما هي في الكود السابق)
    def show_msg(self, title, message):
        MyMessageBox(self, title, message)

    def select_files(self):
        self.file_paths = filedialog.askopenfilenames(title=fix_ar("choose files "), 
                                                       filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if self.file_paths:
            self.files_text.delete("0.0", "end")
            for i, path in enumerate(self.file_paths, 1):
                self.files_text.insert("end", f"{i}. {os.path.basename(path)}\n")
            self.status_label.configure(text=fix_ar(f"تم اختيار {len(self.file_paths)} documents"))
        
    def convert_to_pdf(self):
        if not self.file_paths:
            self.show_msg("warning", "Please choose files first!")
            return

        save_path = filedialog.asksaveasfilename(title=fix_ar("حفظ الملف باسم"), defaultextension=".pdf")
        if not save_path: return

        try:
            self.status_label.configure(text=fix_ar("جاري المعالجة والضغط... انتظر قليلاً"))
            self.update_idletasks()

            images = [Image.open(p).convert('RGB') for p in self.file_paths]
            quality = 95
            images[0].save(save_path, save_all=True, append_images=images[1:], optimize=True, quality=quality)
            
            file_size = os.path.getsize(save_path) / (1024 * 1024)
            while file_size > 1.9 and quality > 30:
                quality -= 10
                images[0].save(save_path, save_all=True, append_images=images[1:], optimize=True, quality=quality)
                file_size = os.path.getsize(save_path) / (1024 * 1024)

            msg = f"تم الحفظ بنجاح! الحجم: {file_size:.2f} MB"
            self.show_msg("نجاح", msg)
            self.status_label.configure(text=fix_ar(msg))
            
        except Exception as e:
            self.show_msg("خطأ", f"حدث خطأ: {str(e)}")

if __name__ == "__main__":
    app = HousingPDFApp()
    app.mainloop()