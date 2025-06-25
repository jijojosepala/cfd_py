import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox
import json, os
from datetime import datetime

DATA_FILE = "data.json"

# Load or initialize data
data = {}
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)

def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

class FileFlowApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FileFlow - Offline")
        self.root.geometry("1020x650")
        self.view_completed = False

        self.create_ui()
        self.refresh_file_list()

    def create_ui(self):
        # Top toolbar
        top_frame = tb.Frame(self.root, padding=10)
        top_frame.pack(fill=X)

        self.toggle_btn = tb.Button(top_frame, text="📁 View Completed Files", bootstyle=SECONDARY, command=self.toggle_view)
        self.toggle_btn.pack(side=LEFT)

        create_btn = tb.Button(top_frame, text="➕ Create New File", bootstyle=PRIMARY, command=self.create_new_file)
        create_btn.pack(side=RIGHT)

        self.tab_label = tb.Label(self.root, text="Incomplete Files", font=("Segoe UI", 14, "bold"), bootstyle=INFO)
        self.tab_label.pack(anchor="w", padx=15, pady=(5, 0))

        # Card container
        self.card_container = tb.Frame(self.root)
        self.card_container.pack(fill=BOTH, expand=True, padx=15, pady=10)

    def toggle_view(self):
        self.view_completed = not self.view_completed
        if self.view_completed:
            self.tab_label.config(text="Completed Files")
            self.toggle_btn.config(text="📂 View Incomplete Files")
        else:
            self.tab_label.config(text="Incomplete Files")
            self.toggle_btn.config(text="📁 View Completed Files")
        self.refresh_file_list()

    def refresh_file_list(self):
        for widget in self.card_container.winfo_children():
            widget.destroy()

        for file_id, info in data.items():
            is_complete = info.get("status", "").lower() == "completed"
            if is_complete != self.view_completed:
                continue
            self.create_file_card(file_id, info)

    def create_file_card(self, file_id, info):
        frame = tb.Frame(self.card_container, relief="solid", borderwidth=1, padding=10)
        frame.pack(fill=X, pady=6)

        title = tb.Label(frame, text=info.get("title", "Untitled"), font=("Segoe UI", 12, "bold"))
        title.pack(anchor="w")

        id_label = tb.Label(frame, text=file_id, bootstyle=SECONDARY)
        id_label.pack(anchor="w")

        type_label = tb.Label(frame, text=info.get("type", ""), bootstyle=("light", "inverse"), padding=4)
        type_label.pack(anchor="w", pady=2)

        status_text = info.get("status", "")
        status_label = tb.Label(frame, text=status_text, bootstyle="info")
        status_label.pack(anchor="w")

        holder = tb.Label(frame, text=f"Current Holder: {info.get('holder', '')}", bootstyle=SECONDARY)
        holder.pack(anchor="w")

        menu_btn = tb.Menubutton(frame, text="⋮", bootstyle=LIGHT)
        menu = tk.Menu(menu_btn, tearoff=0)
        menu.add_command(label="📜 View Timeline", command=lambda: self.view_timeline(file_id))
        menu.add_command(label="✏️ Update Status", command=lambda: self.update_status(file_id))
        if self.view_completed:
            menu.add_command(label="🔁 Mark as Incomplete", command=lambda: self.mark_incomplete(file_id))
        else:
            menu.add_command(label="✅ Mark as Complete", command=lambda: self.mark_complete(file_id))
            menu.add_command(label="📦 GD Completed", command=lambda: self.gd_complete(file_id))
        menu_btn.config(menu=menu)
        menu_btn.pack(anchor="e")

    def create_new_file(self):
        popup = tb.Toplevel(self.root)
        popup.title("Create New File")
        popup.geometry("320x280")

        tb.Label(popup, text="File ID:").pack()
        id_entry = tb.Entry(popup)
        id_entry.pack()

        tb.Label(popup, text="File Name:").pack()
        title_entry = tb.Entry(popup)
        title_entry.pack()

        tb.Label(popup, text="File Type:").pack()
        file_type = tb.Combobox(popup, values=["Cash Purchase", "Local Purchase"])
        file_type.pack()

        def submit():
            fid = id_entry.get().strip()
            title = title_entry.get().strip()
            ftype = file_type.get().strip()
            if fid in data:
                messagebox.showerror("Error", "File ID already exists")
                return
            data[fid] = {
                "title": title,
                "type": ftype,
                "status": "File Created",
                "holder": "",
                "timeline": [
                    {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                     "status": "File Created",
                     "holder": "",
                     "remarks": f"New {ftype.lower()} file created."}
                ]
            }
            save_data()
            popup.destroy()
            self.refresh_file_list()

        tb.Button(popup, text="Create", bootstyle=SUCCESS, command=submit).pack(pady=10)

    def update_status(self, fid):
        popup = tb.Toplevel(self.root)
        popup.title("Update Status")
        popup.geometry("300x220")

        tb.Label(popup, text="New Status").pack()
        status_entry = tb.Entry(popup)
        status_entry.pack()

        tb.Label(popup, text="Current Holder").pack()
        holder_entry = tb.Entry(popup)
        holder_entry.pack()

        tb.Label(popup, text="Remarks (optional)").pack()
        remarks_entry = tb.Entry(popup)
        remarks_entry.pack()

        def submit():
            status = status_entry.get().strip()
            holder = holder_entry.get().strip()
            remarks = remarks_entry.get().strip()
            data[fid]["status"] = status
            data[fid]["holder"] = holder
            data[fid]["timeline"].append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": status,
                "holder": holder,
                "remarks": remarks
            })
            save_data()
            popup.destroy()
            self.refresh_file_list()

        tb.Button(popup, text="Update", bootstyle=PRIMARY, command=submit).pack(pady=10)

    def view_timeline(self, fid):
        popup = tb.Toplevel(self.root)
        popup.title(f"Timeline - {fid}")
        popup.geometry("500x300")
        text = tk.Text(popup, wrap="word")
        text.pack(fill="both", expand=True)
        for entry in data[fid]["timeline"]:
            text.insert("end", f"{entry['status']}\n{entry['remarks']}\nBy {entry['holder']} on {entry['timestamp']}\n\n")
        text.config(state="disabled")

    def mark_complete(self, fid):
        data[fid]["status"] = "Completed"
        data[fid]["timeline"].append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Completed",
            "holder": data[fid].get("holder", ""),
            "remarks": "File marked as complete"
        })
        save_data()
        self.refresh_file_list()

    def mark_incomplete(self, fid):
        data[fid]["status"] = "In Progress"
        data[fid]["timeline"].append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "In Progress",
            "holder": data[fid].get("holder", ""),
            "remarks": "File re-opened"
        })
        save_data()
        self.refresh_file_list()

    def gd_complete(self, fid):
        data[fid]["status"] = "GD Signed"
        data[fid]["holder"] = "Stores"
        data[fid]["timeline"].append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "GD Signed",
            "holder": "Stores",
            "remarks": "GD completed and sent to Stores"
        })
        save_data()
        self.refresh_file_list()

app = FileFlowApp(tb.Window(themename="flatly"))
app.root.mainloop()
