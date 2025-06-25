
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "data.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
else:
    data = {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class FileTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File / Project Tracker")
        self.root.geometry("900x500")
        self.showing_completed = False
        self.selected_file_id = None
        self.setup_ui()

    def setup_ui(self):
        self.toggle_btn = ttk.Button(self.root, text="🔁 View Completed Files", command=self.toggle_files)
        self.toggle_btn.pack(side=tk.TOP, fill=tk.X)

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.left_frame = ttk.Frame(main_frame, width=400)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)

        self.right_frame = ttk.Frame(main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.file_list_label = ttk.Label(self.right_frame, text="Incomplete Files", font=("Arial", 12, "bold"))
        self.file_list_label.pack(anchor="w")

        self.file_listbox = tk.Listbox(self.right_frame, width=40, height=25)
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        self.file_listbox.bind("<<ListboxSelect>>", self.display_selected_file)

        self.timeline_display = tk.Text(self.left_frame, wrap="word", width=60)
        self.timeline_display.pack(fill=tk.BOTH, expand=True)

        self.bottom = ttk.Frame(self.root)
        self.bottom.pack(side=tk.BOTTOM, fill=tk.X)

        ttk.Button(self.bottom, text="➕ New Project", command=self.create_project).pack(side=tk.LEFT, padx=10, pady=10)
        ttk.Button(self.bottom, text="✏️ Update Status", command=self.update_status).pack(side=tk.LEFT, padx=10)
        ttk.Button(self.bottom, text="❌ Exit", command=self.root.quit).pack(side=tk.RIGHT, padx=10)

        self.mark_button = ttk.Button(self.bottom, text="", command=self.toggle_completion_status)
        self.mark_button.pack(side=tk.RIGHT, padx=10)
        self.mark_button.pack_forget()

        self.gd_button = ttk.Button(self.bottom, text="📝 GD Completed", command=self.mark_gd_completed)
        self.gd_button.pack(side=tk.RIGHT, padx=10)
        self.gd_button.pack_forget()

        self.refresh_list()

    def toggle_files(self):
        self.showing_completed = not self.showing_completed
        self.file_list_label.config(text="Completed Files" if self.showing_completed else "Incomplete Files")
        self.toggle_btn.config(text="🔁 View Incomplete Files" if self.showing_completed else "🔁 View Completed Files")
        self.refresh_list()
        self.timeline_display.delete("1.0", tk.END)
        self.mark_button.pack_forget()
        self.gd_button.pack_forget()

    def refresh_list(self):
        self.file_listbox.delete(0, tk.END)
        for fid, info in data.items():
            is_completed = info["status"].lower() == "completed"
            if is_completed == self.showing_completed:
                self.file_listbox.insert(tk.END, f"{fid} - {info['title']}")

    def display_selected_file(self, event):
        if not self.file_listbox.curselection():
            self.mark_button.pack_forget()
            self.gd_button.pack_forget()
            return
        selected = self.file_listbox.get(self.file_listbox.curselection())
        self.selected_file_id = selected.split(" - ")[0]
        file = data[self.selected_file_id]
        self.timeline_display.config(state="normal")
        self.timeline_display.delete("1.0", tk.END)
        self.timeline_display.insert(tk.END, f"File ID: {self.selected_file_id}\nTitle: {file['title']}\nStatus: {file['status']}\nHolder: {file['holder']}\n\nTimeline:\n")
        for entry in file["timeline"]:
            self.timeline_display.insert(tk.END, f"- {entry['timestamp']} | {entry['status']} | {entry['holder']} | {entry['remarks']}\n")
        self.timeline_display.config(state="disabled")

        if self.showing_completed:
            self.mark_button.config(text="⬅️ Mark as Incomplete")
            self.gd_button.pack_forget()
        else:
            self.mark_button.config(text="✅ Mark as Completed")
            self.gd_button.pack(side=tk.RIGHT, padx=10)
        self.mark_button.pack(side=tk.RIGHT, padx=10)

    def toggle_completion_status(self):
        if not self.selected_file_id:
            return
        file = data[self.selected_file_id]
        new_status = "Completed" if not self.showing_completed else "In Progress"
        remarks = "Marked as completed" if new_status == "Completed" else "Reopened"
        file["status"] = new_status
        file["timeline"].append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": new_status,
            "holder": file["holder"],
            "remarks": remarks
        })
        save_data()
        self.refresh_list()
        self.timeline_display.delete("1.0", tk.END)
        self.mark_button.pack_forget()
        self.gd_button.pack_forget()

    def mark_gd_completed(self):
        if not self.selected_file_id:
            return
        file = data[self.selected_file_id]
        file["status"] = "GD Signed"
        file["holder"] = "Stores"
        file["timeline"].append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "GD Signed",
            "holder": "Stores",
            "remarks": "GD completed and forwarded to Stores"
        })
        save_data()
        self.refresh_list()
        self.timeline_display.delete("1.0", tk.END)

    def create_project(self):
        popup = tk.Toplevel(self.root)
        popup.title("Create New File")
        popup.geometry("300x180")

        ttk.Label(popup, text="File ID:").pack()
        file_id_entry = ttk.Entry(popup)
        file_id_entry.pack()

        ttk.Label(popup, text="Title:").pack()
        title_entry = ttk.Entry(popup)
        title_entry.pack()

        def submit():
            file_id = file_id_entry.get().strip()
            title = title_entry.get().strip()
            if not file_id or file_id in data:
                messagebox.showerror("Error", "Invalid or duplicate File ID.")
                return
            data[file_id] = {
                "title": title,
                "status": "In Progress",
                "holder": "Origin",
                "timeline": [{
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "Created",
                    "holder": "Origin",
                    "remarks": "Initial creation"
                }]
            }
            save_data()
            self.refresh_list()
            popup.destroy()

        ttk.Button(popup, text="Create", command=submit).pack(pady=10)

    def update_status(self):
        popup = tk.Toplevel(self.root)
        popup.title("Update File")
        popup.geometry("300x220")

        ttk.Label(popup, text="File ID:").pack()
        file_id_entry = ttk.Entry(popup)
        file_id_entry.pack()

        ttk.Label(popup, text="New Status:").pack()
        status_entry = ttk.Entry(popup)
        status_entry.pack()

        ttk.Label(popup, text="New Holder:").pack()
        holder_entry = ttk.Entry(popup)
        holder_entry.pack()

        ttk.Label(popup, text="Remarks:").pack()
        remarks_entry = ttk.Entry(popup)
        remarks_entry.pack()

        def submit():
            file_id = file_id_entry.get().strip()
            if file_id not in data:
                messagebox.showerror("Error", "File ID not found.")
                return
            entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": status_entry.get().strip(),
                "holder": holder_entry.get().strip(),
                "remarks": remarks_entry.get().strip()
            }
            data[file_id]["status"] = entry["status"]
            data[file_id]["holder"] = entry["holder"]
            data[file_id]["timeline"].append(entry)
            save_data()
            self.refresh_list()
            popup.destroy()

        ttk.Button(popup, text="Update", command=submit).pack(pady=10)

# Run the app
root = tk.Tk()
style = ttk.Style()
style.theme_use("clam")
app = FileTrackerApp(root)
root.mainloop()
