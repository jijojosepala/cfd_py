import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import json
import os
from datetime import datetime

DATA_FILE = "data.json"

# Load or initialize data
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
else:
    data = {}



def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def create_project():
    file_id = simpledialog.askstring("New File/Project", "Enter File/Project ID:")
    if not file_id:
        return
    if file_id in data:
        messagebox.showerror("Error", "File ID already exists.")
        return
    title = simpledialog.askstring("Title", "Enter Project Title:")
    data[file_id] = {
        "title": title,
        "status": "Created",
        "holder": "Origin",
        "timeline": [
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "Created",
                "holder": "Origin",
                "remarks": "Initial creation"
            }
        ]
    }
    save_data()
    messagebox.showinfo("Success", f"Project '{file_id}' created.")

def update_status():
    file_id = simpledialog.askstring("Update File", "Enter File ID:")
    if file_id not in data:
        messagebox.showerror("Error", "File ID not found.")
        return
    status = simpledialog.askstring("Status", "Enter New Status:")
    holder = simpledialog.askstring("Holder", "Enter Current Holder:")
    remarks = simpledialog.askstring("Remarks", "Any Remarks?")
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        "holder": holder,
        "remarks": remarks
    }
    data[file_id]["status"] = status
    data[file_id]["holder"] = holder
    data[file_id]["timeline"].append(entry)
    save_data()
    messagebox.showinfo("Updated", f"Status updated for '{file_id}'.")

def view_timeline():
    file_id = simpledialog.askstring("View Timeline", "Enter File ID:")
    if file_id not in data:
        messagebox.showerror("Error", "File ID not found.")
        return
    timeline = data[file_id]["timeline"]
    timeline_str = f"Timeline for {file_id} - {data[file_id]['title']}\n\n"
    for entry in timeline:
        timeline_str += (f"{entry['timestamp']} | "
                         f"Status: {entry['status']} | "
                         f"Holder: {entry['holder']} | "
                         f"Remarks: {entry['remarks']}\n")
    show_text_window(f"Timeline: {file_id}", timeline_str)

def show_text_window(title, content):
    win = tk.Toplevel(root)
    win.title(title)
    text = tk.Text(win, wrap="word", width=80, height=25)
    text.pack(padx=10, pady=10)
    text.insert("1.0", content)
    text.config(state="disabled")

def list_all_files():
    content = "All Files/Projects:\n\n"
    for fid, info in data.items():
        content += f"{fid} | Title: {info['title']} | Status: {info['status']} | Holder: {info['holder']}\n"
    show_text_window("All Files", content)

# GUI
root = tk.Tk()
root.title("Offline File Tracker")
root.geometry("400x300")

label = tk.Label(root, text="File / Project Tracker", font=("Arial", 16, "bold"))
label.pack(pady=10)

btn1 = tk.Button(root, text="➕ Create New File/Project", width=30, command=create_project)
btn1.pack(pady=5)

btn2 = tk.Button(root, text="✏️ Update File Status", width=30, command=update_status)
btn2.pack(pady=5)

btn3 = tk.Button(root, text="📜 View Timeline", width=30, command=view_timeline)
btn3.pack(pady=5)

btn4 = tk.Button(root, text="📂 List All Files", width=30, command=list_all_files)
btn4.pack(pady=5)

btn_exit = tk.Button(root, text="❌ Exit", width=30, command=root.quit)
btn_exit.pack(pady=20)

root.mainloop()
