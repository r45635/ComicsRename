from tkinter import filedialog

def select_folder():
    folder = filedialog.askdirectory(initialdir="/Volumes")
    # ...existing code...