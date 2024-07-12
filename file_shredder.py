import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os
import shutil
from datetime import datetime
import threading

class FileShredderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Shredder")
        root.resizable(False, False)

        self.bg_color = "#212121"
        self.button_color = "#424242"
        self.text_color = "#ffffff"

        self.frame = tk.Frame(root, bg=self.bg_color)
        self.frame.pack(padx=100, pady=100)

        self.FileShredder_label = tk.Label(self.frame, text="File Shredder", bg=self.bg_color, fg=self.text_color, font=("Helvetica", 20, "bold"))
        self.FileShredder_label.pack(pady=10)

        self.select_file_button = tk.Button(self.frame, text="Select File", command=self.select_file, bg=self.button_color, fg=self.text_color)
        self.select_file_button.pack(pady=10)

        self.select_folder_button = tk.Button(self.frame, text="Select Folder", command=self.select_folder, bg=self.button_color, fg=self.text_color)
        self.select_folder_button.pack(pady=10)

        self.shred_button = tk.Button(self.frame, text="Shred", command=self.confirm_shred, state=tk.DISABLED, bg=self.button_color, fg=self.text_color)
        self.shred_button.pack(pady=10)

        self.progress = ttk.Progressbar(self.frame, orient=tk.HORIZONTAL, length=200, mode='determinate')
        self.progress.pack(pady=10)
        self.progress.pack_forget()

        self.root.config(bg=self.bg_color)

    def select_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.folder_path = None
            self.shred_button.config(state=tk.NORMAL)
            self.check_and_warn_large_file(self.file_path)

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.file_path = None
            self.shred_button.config(state=tk.NORMAL)
            self.check_and_warn_large_folder(self.folder_path)

    def check_and_warn_large_file(self, file_path):
        file_size = os.path.getsize(file_path)
        if file_size > 1000000:
            confirm = messagebox.askyesno("Warning", "Selected file is large. Are you sure you want to shred it?")
            if not confirm:
                self.file_path = None
                self.shred_button.config(state=tk.DISABLED)

    def check_and_warn_large_folder(self, folder_path):
        folder_size = sum(os.path.getsize(os.path.join(root, filename)) for root, _, filenames in os.walk(folder_path) for filename in filenames)
        if folder_size > 100000000:
            confirm = messagebox.askyesno("Warning", "Selected folder is large. Are you sure you want to shred it?")
            if not confirm:
                self.folder_path = None
                self.shred_button.config(state=tk.DISABLED)

    def confirm_shred(self):
        confirm = False
        if self.file_path:
            file_details = f"File: {os.path.basename(self.file_path)}\nSize: {os.path.getsize(self.file_path)} bytes\nLast Modified: {datetime.fromtimestamp(os.path.getmtime(self.file_path))}"
            confirm = messagebox.askyesno("Confirmation", f"Are you sure you want to shred the selected file?\n\n{file_details}")
        elif self.folder_path:
            folder_size = sum(os.path.getsize(os.path.join(root, filename)) for root, _, filenames in os.walk(self.folder_path) for filename in filenames)
            folder_details = f"Folder: {self.folder_path}\nSize: {folder_size} bytes"
            confirm = messagebox.askyesno("Confirmation", f"Are you sure you want to shred the selected folder?\n\n{folder_details}")

        if confirm:
            if self.file_path:
                self.start_shredding(self.shred_file)
            elif self.folder_path:
                self.start_shredding(self.shred_folder)

    def start_shredding(self, shred_function):
        self.progress.pack(pady=10)
        self.shred_button.config(state=tk.DISABLED)
        threading.Thread(target=shred_function).start()

    def shred_file(self):
        try:
            with open(self.file_path, "rb+") as f:
                file_size = os.path.getsize(self.file_path)
                patterns = [
                    b'\x55', b'\xAA', b'\x92', b'\x49', b'\x24', b'\x12', b'\x89', b'\x49',
                    b'\x24', b'\x92', b'\x49', b'\x24', b'\x6D', b'\xB6', b'\xDB', b'\x6D',
                    b'\xB6', b'\xDB', b'\x49', b'\x24', b'\x92', b'\x49', b'\x24', b'\x55',
                    b'\xAA', b'\x92', b'\x49', b'\x24', b'\x12', b'\x89', b'\x49', b'\x24',
                    b'\x92', b'\49', b'\x24', b'\x6D'
                ]

                for i in range(35):
                    f.seek(0)
                    for pattern in patterns:
                        f.write(pattern * (file_size // len(pattern) + 1))
                    f.seek(0)
                    self.update_progress((i + 1) * 100 // 35)

                f.truncate()

            os.remove(self.file_path)
            self.progress.pack_forget()
            self.shred_button.config(state=tk.NORMAL)
            messagebox.showinfo("Success", "File shredded successfully!")
        except FileNotFoundError:
            self.progress.pack_forget()
            self.shred_button.config(state=tk.NORMAL)
            messagebox.showerror("Error", "File not found.")
        except Exception as e:
            self.progress.pack_forget()
            self.shred_button.config(state=tk.NORMAL)
            messagebox.showerror("Error", f"An error occurred: {e}")

    def shred_folder(self):
        try:
            current_directory = os.getcwd()
            if self.folder_path != current_directory:
                shutil.rmtree(self.folder_path)
                self.progress.pack_forget()
                self.shred_button.config(state=tk.NORMAL)
                messagebox.showinfo("Success", "Folder shredded successfully!")
            else:
                self.progress.pack_forget()
                self.shred_button.config(state=tk.NORMAL)
                messagebox.showerror("Error", "Cannot shred the program directory!")
        except FileNotFoundError:
            self.progress.pack_forget()
            self.shred_button.config(state=tk.NORMAL)
            messagebox.showerror("Error", "Folder not found.")
        except Exception as e:
            self.progress.pack_forget()
            self.shred_button.config(state=tk.NORMAL)
            messagebox.showerror("Error", f"An error occurred: {e}")

    def update_progress(self, value):
        self.progress['value'] = value
        self.root.update_idletasks()

root = tk.Tk()
app = FileShredderApp(root)
root.mainloop()