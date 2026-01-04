import shutil
from pathlib import Path
from tkinter import *
from tkinter import ttk

import winsound
from pynput import keyboard
from PIL import Image, ImageTk

VERSION = "0.1.0"

# The utility should be in the BB save data directory, this logic will change in the future
SAVE_DIR = Path.cwd()
BB_CUSA = "CUSA00207"
BACKUP_DIR = SAVE_DIR / (BB_CUSA + "_backup")


def backup_save() -> None:
    """
    Backs up game save data to the backup directory.

    Copies the specific CUSA folder from the source to the backup location.
    Displays a success message on completion or an error message if the
    source files are missing.
    """
    try:
        shutil.copytree(SAVE_DIR / BB_CUSA, BACKUP_DIR, dirs_exist_ok=True)
        success_message("Files backed up successfully")
    except FileNotFoundError:
        error_message()


def restore_save() -> None:
    """
    Restores game save data from the backup directory.

    Copies the specific CUSA folder from the backup directory to the source.
    Displays a success message on completion or an error message if the
    backup files are missing.
    """
    try:
        shutil.copytree(BACKUP_DIR, SAVE_DIR / BB_CUSA, dirs_exist_ok=True)
        success_message("Files restored successfully")
    except FileNotFoundError:
        error_message()


def success_message(message: str) -> None:
    """Displays a success message on the app interface and beeps."""
    winsound.MessageBeep(winsound.MB_OK)
    status_label.config(text=message, fg="green")
    root.after(2000, lambda: status_label.config(text=""))


def error_message() -> None:
    """Displays an error message on the app interface and beeps."""
    winsound.MessageBeep(winsound.MB_ICONHAND)
    status_label.config(text="Files not found!", fg="red")
    root.after(2000, lambda: status_label.config(text=""))


root = Tk()
root.title("Bloodborne Save Manager")
# root.geometry("300x150")
root.resizable(False, False)

mainframe = ttk.Frame(root, padding=(5, 10, 5, 10))
mainframe.grid(column=0, row=0, sticky="N W E S")

button_frame = ttk.Frame(root, padding=(50, 10, 50, 10))
button_frame.grid(column=0, row=1, sticky="N W E S")

logo_open = Image.open("images/bsm_logo.jpg")
logo_resized = logo_open.resize((300, 100))
logo_tk = ImageTk.PhotoImage(logo_resized)

key_info = "Press F5 to backup save files\nPress F8 to restore save files"
ttk.Label(mainframe, text=key_info, image=logo_tk, compound="top").grid(column=1, row=0, columnspan=2)

status_label = Label(mainframe, text="")
status_label.grid(column=1, row=1, columnspan=2, pady=10)

ttk.Button(button_frame, text="BackUp", command=backup_save).grid(
    column=1, row=2, sticky=W
)
ttk.Button(button_frame, text="Restore", command=restore_save).grid(
    column=2, row=2, sticky=E
)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
mainframe.columnconfigure(2, weight=1)
button_frame.columnconfigure(2, weight=1)


def on_press(key: keyboard.Key) -> None:
    """
    Listens for special key presses on the keyboard.

    F5 - backups the specified CUSA folder.
    F6 - restores the specified CUSA folder.
    F12 - closes the application.
    """
    if key == keyboard.Key.f5:
        backup_save()
    elif key == keyboard.Key.f8:
        restore_save()
    elif key == keyboard.Key.f12:
        root.destroy()
    return None


listener = keyboard.Listener(on_press=on_press)
listener.start()

root.mainloop()
