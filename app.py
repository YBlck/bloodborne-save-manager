import configparser
import os
import shutil
import sys
from pathlib import Path
from tkinter import *
from tkinter import ttk

import winsound
from PIL import Image, ImageTk
from pynput import keyboard

VERSION = "0.2.0"

CONFIG = configparser.ConfigParser()
CONFIG.read("config.ini")

# The utility should be in the BB save data directory, this logic will change in the future
SAVE_DIR = Path.cwd()
BB_CUSA = "CUSA00207"
BACKUP_DIR = SAVE_DIR / (BB_CUSA + "_backup")

HOTKEYS = {
    "backup": CONFIG.get("hotkeys", "backup", fallback="f5"),
    "restore": CONFIG.get("hotkeys", "restore", fallback="f8"),
    "exit": CONFIG.get("hotkeys", "exit", fallback="f12"),
}


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


def resource_path(relative_path: str) -> str:
    """
    Returns the absolute path to resource, works for dev and for PyInstaller.
    """
    try:
        # PyInstaller creates a temporary folder and stores the path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # If we run just a .py file, we use the current directory
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


root = Tk()
root.title("Bloodborne Save Manager")
root.iconbitmap(resource_path("images/bsm_icon.ico"))
root.resizable(False, False)

mainframe = ttk.Frame(root, padding=(5, 10, 5, 10))
mainframe.grid(column=0, row=0, sticky="N W E S")

button_frame = ttk.Frame(root, padding=(50, 10, 50, 10))
button_frame.grid(column=0, row=1, sticky="N W E S")

logo_open = Image.open(resource_path("images/bsm_logo.jpg"))
logo_resized = logo_open.resize((300, 100))
logo_tk = ImageTk.PhotoImage(logo_resized)

key_info = (f"Press '{HOTKEYS["backup"].upper()}' to backup save files\n"
            f"Press '{HOTKEYS["restore"].upper()}' to restore save files")
ttk.Label(mainframe, text=key_info, image=logo_tk, compound="top").grid(
    column=1, row=0, columnspan=2
)

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


def on_press(key_in: keyboard.Key | keyboard.KeyCode) -> None:
    """
    Listens for special key presses on the keyboard.

    Default keys:
    F5 - backups the specified CUSA folder.
    F6 - restores the specified CUSA folder.
    F12 - closes the application.
    """
    key = (
        key_in.name
        if hasattr(key_in, "name")
        else str(key_in).replace("'", "")
    )

    if key.lower() == HOTKEYS["backup"].lower():
        backup_save()
    elif key.lower() == HOTKEYS["restore"].lower():
        restore_save()
    elif key.lower() == HOTKEYS["exit"].lower():
        root.destroy()
    return None


listener = keyboard.Listener(on_press=on_press)
listener.start()

root.mainloop()
