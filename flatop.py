import subprocess
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

# Magic starts here (god forbid)

class AutocompleteEntry(ttk.Entry):
    def __init__(self, master, completions, icon_label, **kwargs):
        super().__init__(master, **kwargs)
        self.completions = completions
        self.bind('<KeyRelease>', self.check_completion)
        self.listbox = tk.Listbox(master)
        self.listbox.bind('<Double-Button-1>', self.select_completion)
        self.icon_label = icon_label

    def check_completion(self, event):
        text = self.get()
        if text == '':
            self.listbox.delete(0, tk.END)
            self.listbox.place_forget()
            self.icon_label.config(image='')
        else:
            matches = [item for item in self.completions if text.lower() in item.lower()]
            if matches:
                self.listbox.delete(0, tk.END)
                for match in matches:
                    self.listbox.insert(tk.END, match)
                self.listbox.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
            else:
                self.listbox.place_forget()
                self.icon_label.config(image='')

    def select_completion(self, event):
        if self.listbox.curselection():
            selected_app = self.listbox.get(self.listbox.curselection())
            self.delete(0, tk.END)
            self.insert(0, selected_app)
            self.listbox.place_forget()
            icon_path = find_flatpak_icon(selected_app)
            if icon_path:
                image = Image.open(icon_path)
                image = image.resize((48, 48), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.icon_label.config(image=photo)
                self.icon_label.image = photo
            else:
                self.icon_label.config(image='')

# Magic ends here. From now on it is simple I promise.

def get_flatpak_apps():
    result = subprocess.run(['flatpak', 'list', '--app', '--columns=application'], capture_output=True, text=True)
    return result.stdout.strip().split('\n')

def find_flatpak_icon(app_id):
    try:
        # Get installation path
        install_path_result = subprocess.run(['flatpak', 'info', '--show-location', app_id], capture_output=True, text=True)
        install_path = install_path_result.stdout.strip()

        # Search common icon directories
        icon_sizes = ['512x512', '256x256', '128x128', '64x64', '48x48', '32x32', '24x24', '16x16']
        icon_extensions = ['png', 'svg']

        for size in icon_sizes:
            for ext in icon_extensions:
                icon_path = os.path.join(install_path, f'files/share/icons/hicolor/{size}/apps/{app_id}.{ext}')
                if os.path.exists(icon_path):
                    return icon_path

        # Fallback to scalable icons directory
        for ext in icon_extensions:
            icon_path = os.path.join(install_path, f'files/share/icons/hicolor/scalable/apps/{app_id}.{ext}')
            if os.path.exists(icon_path):
                return icon_path

    except Exception as weewoo:
        print(f"Error finding icon for {app_id}: {weewoo}")
    return None

def create_shortcut(name, comment, entry, terminal):

    needs_terminal = terminal.get()

    if needs_terminal:
        structure = f"[Desktop Entry]\nName={name.get()}\nComment={comment.get()}\nExec=flatpak run {entry.get()}\nTerminal=true\nType=Application\nIcon={entry.get()}"

    else:
        structure = f"[Desktop Entry]\nName={name.get()}\nComment={comment.get()}\nExec=flatpak run {entry.get()}\nTerminal=false\nType=Application\nIcon={entry.get()}"


    desktop_path = os.path.expanduser("~/Desktop")
    file_path = os.path.join(desktop_path, f"{name.get()}.desktop")

    with open(file_path, 'w') as file:
        file.write(structure)

def main():
    root = tk.Tk()
    root.title("Flatpak Desktop Shortcut Creator")

    flatpak_apps = get_flatpak_apps()

    name_label = tk.Label(root, text="Shortcut name:")
    name_label.grid(row=0, column=1, padx=5, pady=5)

    name = tk.Entry(root)
    name.grid(row=0, column=2, padx=5, pady=5)

    comment_label = tk.Label(root, text="Comment/description:")
    comment_label.grid(row=1, column=1, padx=5, pady=5)

    comment = tk.Entry(root)
    comment.grid(row=1, column=2, padx=5, pady=5)

    icon_label = tk.Label(root)
    icon_label.grid(row=4, column=2, padx=5, pady=5)

    entry_label = ttk.Label(root, text="Flatpak app:")
    entry_label.grid(row=2, column=1, padx=5, pady=5)

    entry = AutocompleteEntry(root, flatpak_apps, icon_label)
    entry.grid(row=2, column=2, padx=5, pady=5)

    terminal = tk.BooleanVar()

    terminal_checkbox = tk.Checkbutton(root, text="Needs terminal", variable=terminal)
    terminal_checkbox.grid(row=3, column=1, padx=5, pady=5)

    create_button = tk.Button(root, text="Create Desktop Shortcut", command=lambda: create_shortcut(name, comment, entry, terminal))
    create_button.grid(row=4, columnspan=2, padx=5, pady=30)

    root.mainloop()

if __name__ == "__main__":
    main()