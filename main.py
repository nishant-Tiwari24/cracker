import os
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter.ttk import Progressbar, Style, Button, Label, Entry
import threading
from slide_extractor import SlideExtractor
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class SlideExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Slide Extractor")
        self.root.geometry("800x600")
        self.root.configure(bg="#f4f4f9")
        self.style = Style()
        self.style.theme_use('clam')

        self.create_widgets()

    def create_widgets(self):
        self.center_frame = tk.Frame(self.root, bg="#f4f4f9")
        self.center_frame.pack(expand=True)

        Label(self.center_frame, text="Enter YouTube URL:", font=("Helvetica", 16, "bold"), background="#f4f4f9").grid(row=0, column=0, pady=20, padx=20, sticky="w")
        self.url_entry = Entry(self.center_frame, width=50, font=("Helvetica", 16))
        self.url_entry.grid(row=0, column=1, pady=10, padx=20)

        Label(self.center_frame, text="Frame Interval (Seconds):", font=("Helvetica", 16, "bold"), background="#f4f4f9").grid(row=1, column=0, pady=20, padx=20, sticky="w")
        self.interval_entry = Entry(self.center_frame, width=10, font=("Helvetica", 16))
        self.interval_entry.insert(0, "5")
        self.interval_entry.grid(row=1, column=1, pady=10, padx=20)

        Label(self.center_frame, text="Similarity Threshold (0.0 to 1.0):", font=("Helvetica", 16, "bold"), background="#f4f4f9").grid(row=2, column=0, pady=20, padx=20, sticky="w")
        self.threshold_entry = Entry(self.center_frame, width=10, font=("Helvetica", 16))
        self.threshold_entry.insert(0, "0.9")
        self.threshold_entry.grid(row=2, column=1, pady=10, padx=20)

        Label(self.center_frame, text="Output Directory: slides/", font=("Helvetica", 16), background="#f4f4f9").grid(row=3, column=0, pady=20, padx=20, sticky="w")

        self.progress_label = Label(self.center_frame, text="Status: Ready", font=("Helvetica", 16), background="#f4f4f9")
        self.progress_label.grid(row=4, column=0, pady=20, padx=20, sticky="w")

        self.progress_bar = Progressbar(self.center_frame, orient="horizontal", length=500, mode="indeterminate")
        self.progress_bar.grid(row=4, column=1, pady=20, padx=20)

        self.extract_button = Button(self.center_frame, text="Extract Slides", style="Accent.TButton", command=self.extract_slides)
        self.extract_button.grid(row=5, column=0, columnspan=2, pady=30)

        self.pdf_button = Button(self.center_frame, text="Generate PDF", style="Accent.TButton", command=self.generate_pdf)
        self.pdf_button.grid(row=6, column=0, columnspan=2, pady=20)

        self.style.configure("Accent.TButton", font=("Helvetica", 16, "bold"), padding=15, background="#4CAF50", foreground="white")
        self.style.map("Accent.TButton", background=[("active", "#45a049")])

    def extract_slides(self):
        url = self.url_entry.get()
        interval = int(self.interval_entry.get())
        threshold = float(self.threshold_entry.get())

        self.toggle_inputs(state="disabled")
        self.progress_label.config(text="Status: Downloading video...")
        self.progress_bar.start()

        threading.Thread(target=self.start_slide_extraction, args=(url, interval, threshold), daemon=True).start()

    def start_slide_extraction(self, url, interval, threshold):
        try:
            extractor = SlideExtractor(video_url=url, interval=interval, similarity_threshold=threshold)
            success = extractor.extract_slides()
            status = "Extraction Complete!" if success else "Extraction Failed!"
            self.progress_label.config(text=f"Status: {status}")
        except Exception as e:
            self.progress_label.config(text=f"Error: {str(e)}")
        finally:
            self.progress_bar.stop()
            self.toggle_inputs(state="normal")

    def toggle_inputs(self, state):
        """Enable or disable input fields and buttons."""
        self.url_entry.config(state=state)
        self.interval_entry.config(state=state)
        self.threshold_entry.config(state=state)
        self.extract_button.config(state=state)

    def generate_pdf(self):
        slide_folder = "slides"
        pdf_filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])

        if not pdf_filename:
            return

        try:
            c = canvas.Canvas(pdf_filename, pagesize=letter)
            c.setFont("Helvetica", 16)

            slide_images = sorted(f for f in os.listdir(slide_folder) if f.endswith(".png"))

            y = 750
            for slide in slide_images:
                slide_path = os.path.join(slide_folder, slide)
                img = Image.open(slide_path)
                img_width, img_height = img.size
                aspect_ratio = (img_height * 500) / img_width
                c.drawImage(slide_path, 50, y, width=500, height=aspect_ratio)

                y -= 550
                if y < 100:
                    c.showPage()
                    y = 750

            c.save()
            messagebox.showinfo("Success", f"PDF generated successfully at:\n{pdf_filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error generating PDF: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SlideExtractorApp(root)
    root.mainloop()
