import configparser
import os
import shutil
import sys
from pathlib import Path
from tkinter import *
from tkinter import ttk, filedialog

import winsound
from PIL import Image, ImageTk
from pynput import keyboard

VERSION = "0.4.0"

CONFIG = configparser.ConfigParser()
CONFIG_FILE = "config.ini"

if not os.path.exists(CONFIG_FILE):
    CONFIG["settings"] = {
        "id": "CUSA00207",
        "path": Path.cwd(),
        "backup": "f5",
        "restore": "f8",
        "exit": "f12",
    }

    with open(CONFIG_FILE, "w") as file:
        CONFIG.write(file)
else:
    CONFIG.read(CONFIG_FILE)


SAVE_DIR = Path(CONFIG.get("settings", "path", fallback=Path.cwd()))
GAME_ID = CONFIG.get("settings", "id", fallback="CUSA00207")
BACKUP_DIR = SAVE_DIR / (GAME_ID + "_backup")

HOTKEYS = {
    "backup": CONFIG.get("settings", "backup", fallback="f5"),
    "restore": CONFIG.get("settings", "restore", fallback="f8"),
    "exit": CONFIG.get("settings", "exit", fallback="f12"),
}


def backup_save() -> None:
    """
    Backs up game save data to the backup directory.

    Copies the specific CUSA folder from the source to the backup location.
    Displays a success message on completion or an error message if the
    source files are missing.
    """
    try:
        shutil.copytree(SAVE_DIR / GAME_ID, BACKUP_DIR, dirs_exist_ok=True)
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
        shutil.copytree(BACKUP_DIR, SAVE_DIR / GAME_ID, dirs_exist_ok=True)
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


def settings() -> None:
    settings_window = Toplevel()
    settings_window.title("Settings")
    settings_window.iconbitmap(resource_path("images/bsm_settings.ico"))
    settings_window.resizable(False, False)
    settings_window.grab_set()
    settings_window.columnconfigure(0, weight=1)

    # Save game path and game ID configuration
    settings_window.save_path = StringVar(value=str(SAVE_DIR))
    settings_window.game_id = StringVar(value=GAME_ID)

    path_frame = ttk.Frame(settings_window, padding=(5, 10, 5, 10))
    path_frame.grid(column=0, row=0, sticky="N W E S")
    path_frame.columnconfigure(1, weight=1)

    ttk.Label(path_frame, text="Saves dir:", width=10).grid(
        column=0, row=0, sticky="E", padx=2
    )
    path_entry = ttk.Entry(path_frame, textvariable=settings_window.save_path)
    path_entry.grid(column=1, row=0, sticky="W E")

    ttk.Label(path_frame, text="Game ID:", width=10).grid(
        column=0, row=1, sticky="E", padx=2
    )
    game_id_entry = ttk.Entry(path_frame, textvariable=settings_window.game_id)
    game_id_entry.grid(column=1, row=1, sticky="W E")

    def browse_folder() -> None:
        selected_directory = filedialog.askdirectory()
        if selected_directory:
            settings_window.save_path.set(selected_directory)

    ttk.Button(path_frame, text="Browse", command=browse_folder).grid(
        column=2, row=0, sticky="W"
    )

    # Hotkeys configuration
    hotkeys_frame = ttk.Frame(settings_window, padding=(5, 10, 5, 10))
    hotkeys_frame.grid(column=0, row=1, sticky="N W E S")
    hotkeys_frame.columnconfigure((1, 3, 5), weight=1)

    settings_window.backup_var = StringVar(value=HOTKEYS["backup"].upper())
    settings_window.restore_var = StringVar(value=HOTKEYS["restore"].upper())
    settings_window.exit_var = StringVar(value=HOTKEYS["exit"].upper())

    f_keys = [f"F{num}" for num in range(1, 13)]

    def update_menus(event=None) -> None:
        b = settings_window.backup_var.get()
        r = settings_window.restore_var.get()
        e = settings_window.exit_var.get()

        backup_combo["values"] = [k for k in f_keys if k not in [r, e]]
        restore_combo["values"] = [k for k in f_keys if k not in [b, e]]
        exit_combo["values"] = [k for k in f_keys if k not in [b, r]]

    ttk.Label(hotkeys_frame, text="Backup:").grid(column=0, row=0, padx=2)
    backup_combo = ttk.Combobox(
        hotkeys_frame,
        textvariable=settings_window.backup_var,
        width=5,
        state="readonly",
    )
    backup_combo.grid(column=1, row=0, padx=5)

    ttk.Label(hotkeys_frame, text="Restore:").grid(column=2, row=0, padx=2)
    restore_combo = ttk.Combobox(
        hotkeys_frame,
        textvariable=settings_window.restore_var,
        width=5,
        state="readonly",
    )
    restore_combo.grid(column=3, row=0, padx=5)

    ttk.Label(hotkeys_frame, text="Exit:").grid(column=4, row=0, padx=2)
    exit_combo = ttk.Combobox(
        hotkeys_frame,
        textvariable=settings_window.exit_var,
        width=5,
        state="readonly",
    )
    exit_combo.grid(column=5, row=0, padx=5)

    backup_combo.bind("<<ComboboxSelected>>", update_menus)
    restore_combo.bind("<<ComboboxSelected>>", update_menus)
    exit_combo.bind("<<ComboboxSelected>>", update_menus)

    update_menus()

    def save_settings() -> None:
        CONFIG["settings"] = {
            "id": settings_window.game_id.get(),
            "path": settings_window.save_path.get(),
            "backup": settings_window.backup_var.get(),
            "restore": settings_window.restore_var.get(),
            "exit": settings_window.exit_var.get(),
        }

        with open(CONFIG_FILE, "w") as settingsfile:
            CONFIG.write(settingsfile)

        settings_window.destroy()

        os.execl(sys.executable, sys.executable, *sys.argv)

    # Buttons
    btn_frame = ttk.Frame(settings_window, padding=(5, 10, 5, 5))
    btn_frame.grid(column=0, row=2, sticky="W E")
    btn_frame.columnconfigure(0, weight=1)
    btn_frame.columnconfigure(1, weight=1)

    btn_ok = ttk.Button(btn_frame, text="OK", command=save_settings)
    btn_ok.grid(column=0, row=2, pady=10, padx=10, sticky="E")

    btn_cancel = ttk.Button(
        btn_frame, text="Cancel", command=settings_window.destroy
    )
    btn_cancel.grid(column=1, row=2, pady=10, padx=10, sticky="W")


root = Tk()
root.title("Bloodborne Save Manager")
root.iconbitmap(resource_path("images/bsm_icon.ico"))
root.resizable(False, False)

mainframe = ttk.Frame(root, padding=(5, 10, 5, 10))
mainframe.grid(column=0, row=0, sticky="N W E S")

button_frame = ttk.Frame(root, padding=(30, 10, 30, 10))
button_frame.grid(column=0, row=1, sticky="N W E S")

logo_open = Image.open(resource_path("images/bsm_logo.jpg"))
logo_resized = logo_open.resize((300, 100))
logo_tk = ImageTk.PhotoImage(logo_resized)

key_info = (
    f"Press '{HOTKEYS["backup"].upper()}' to backup save files\n"
    f"Press '{HOTKEYS["restore"].upper()}' to restore save files"
)
ttk.Label(mainframe, text=key_info, image=logo_tk, compound="top").grid(
    column=1, row=0, columnspan=2
)

status_label = Label(mainframe, text="")
status_label.grid(column=1, row=1, columnspan=2, pady=10)

ttk.Button(button_frame, text="BackUp", command=backup_save).grid(
    column=1, row=2, sticky="W"
)
ttk.Button(button_frame, text="Restore", command=restore_save).grid(
    column=2, row=2
)
ttk.Button(button_frame, text="Settings", command=settings).grid(
    column=3, row=2, sticky="E"
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
