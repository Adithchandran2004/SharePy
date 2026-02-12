import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox

script_dir = os.path.dirname(os.path.abspath(__file__))
queue_path = os.path.join(script_dir, "file_queue.json")


def add_to_queue(selected_files, append=True):
    """Add selected files to queue.json. Append or overwrite based on `append`."""
    file_paths = []

    for path in selected_files:
        path = path.strip()
        if os.path.isfile(path):
            abs_path = os.path.abspath(path)
            file_paths.append(abs_path)

    # Load existing data if appending
    if append and os.path.exists(queue_path):
        try:
            with open(queue_path, "r") as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            existing_data = []
    else:
        existing_data = []

    # Add only unique new files
    data_to_add = []
    for path in file_paths:
        if not any(entry["path"] == path for entry in existing_data):
            data_to_add.append({"path": path, "status": "pending"})

    existing_data.extend(data_to_add)

    with open(queue_path, "w") as f:
        json.dump(existing_data, f, indent=4)

    messagebox.showinfo("Queue Updated", f"Added {len(data_to_add)} new files to queue.")


# ------------------------ GUI Functions ------------------------ #
def browse_folder():
    folder = filedialog.askdirectory(title="Select a Folder")
    if folder:
        file_list.delete(0, tk.END)
        for f in os.listdir(folder):
            path = os.path.join(folder, f)
            if os.path.isfile(path):
                file_list.insert(tk.END, path)


def add_selected():
    selected_indices = file_list.curselection()
    for i in selected_indices:
        path = file_list.get(i)
        if path not in selected_files:
            selected_files.append(path)
            selected_list.insert(tk.END, path)
        else:
            messagebox.showinfo("Duplicate", f"{path} is already added.")


def clear_selected():
    selected_files.clear()
    selected_list.delete(0, tk.END)


def queue_files():
    if not selected_files:
        messagebox.showwarning("No Files", "Please add files to the list before sending.")
        return
    add_to_queue(selected_files, append=True)


# ------------------------ GUI Setup ------------------------ #
root = tk.Tk()
root.title("Persistent File Selector")
root.geometry("600x400")

selected_files = []

btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Browse Folder", command=browse_folder).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Add Selected", command=add_selected).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Clear List", command=clear_selected).grid(row=0, column=2, padx=5)
tk.Button(btn_frame, text="Send", command=queue_files).grid(row=0, column=3, padx=5)

list_frame = tk.Frame(root)
list_frame.pack(fill=tk.BOTH, expand=True)

file_list = tk.Listbox(list_frame, selectmode=tk.MULTIPLE)
file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

selected_list = tk.Listbox(list_frame)
selected_list.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

root.mainloop()

