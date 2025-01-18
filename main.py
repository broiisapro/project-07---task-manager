import customtkinter as ctk
import json
from datetime import datetime
from tkinter import messagebox, simpledialog


TASKS_FILE = "tasks_v2.json"


def load_tasks():
    try:
        with open(TASKS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_tasks(tasks):
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=4)


def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced To-Do List")
        self.tasks = load_tasks()
        self.theme = "light"

        ctk.set_appearance_mode("light")

        self.create_toolbar()
        self.create_task_frame()
        self.refresh_task_list()

    def create_toolbar(self):
        toolbar = ctk.CTkFrame(self.root)
        toolbar.pack(side="top", fill="x", padx=10, pady=5)

        self.add_task_button = ctk.CTkButton(toolbar, text="Add Task", command=self.add_task)
        self.add_task_button.pack(side="left", padx=5, pady=5)

        self.delete_task_button = ctk.CTkButton(toolbar, text="Delete Task", command=self.delete_task)
        self.delete_task_button.pack(side="left", padx=5, pady=5)

        self.mark_complete_button = ctk.CTkButton(toolbar, text="Mark Complete", command=self.mark_complete)
        self.mark_complete_button.pack(side="left", padx=5, pady=5)

        self.filter_button = ctk.CTkButton(toolbar, text="Filter", command=self.filter_tasks)
        self.filter_button.pack(side="left", padx=5, pady=5)

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(toolbar, textvariable=self.search_var, width=250)
        self.search_entry.insert(0, "Search...")
        self.search_entry.pack(side="right", padx=5, pady=5)
        self.search_entry.bind("<FocusIn>", lambda e: self.search_entry.delete(0, "end"))
        self.search_entry.bind("<Return>", lambda e: self.search_tasks())

        self.search_button = ctk.CTkButton(toolbar, text="Search", command=self.search_tasks)
        self.search_button.pack(side="right", padx=5, pady=5)

        self.dark_mode_checkbox = ctk.CTkCheckBox(toolbar, text="Dark Mode", command=self.toggle_theme)
        self.dark_mode_checkbox.pack(side="right", padx=5, pady=5)

    def create_task_frame(self):
        self.task_frame = ctk.CTkFrame(self.root)
        self.task_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.scrollable_frame = ctk.CTkScrollableFrame(self.task_frame)
        self.scrollable_frame.pack(fill="both", expand=True)

    def toggle_theme(self):
        if ctk.get_appearance_mode() == "light":
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")

    def refresh_task_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for task in self.tasks:
            task_frame = ctk.CTkFrame(self.scrollable_frame)
            task_frame.pack(fill="x", pady=5)

            task_label = ctk.CTkLabel(task_frame, text=f"{task['name']} - {task['category']} - {task['deadline']}", anchor="w", width=300)
            task_label.pack(side="left", padx=5)

            task_status = "✓" if task['completed'] else "✗"
            status_label = ctk.CTkLabel(task_frame, text=f"Completed: {task_status}", anchor="w")
            status_label.pack(side="left", padx=5)

            priority_label = ctk.CTkLabel(task_frame, text=f"Priority: {task['priority']}", anchor="w")
            priority_label.pack(side="left", padx=5)

    def add_task(self):
        new_window = ctk.CTkToplevel(self.root)
        new_window.title("Add Task")

        fields = [("Task Name", "name"), ("Deadline (YYYY-MM-DD)", "deadline"), ("Category", "category")]
        entries = {}

        for i, (label_text, key) in enumerate(fields):
            ctk.CTkLabel(new_window, text=label_text).grid(row=i, column=0, sticky="w", padx=5, pady=5)
            entry = ctk.CTkEntry(new_window)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[key] = entry

        ctk.CTkLabel(new_window, text="Priority:").grid(row=len(fields), column=0, sticky="w", padx=5, pady=5)
        priority = ctk.CTkComboBox(new_window, values=["High", "Medium", "Low"])
        priority.grid(row=len(fields), column=1, padx=5, pady=5)
        entries["priority"] = priority

        ctk.CTkLabel(new_window, text="Recurring (Days):").grid(row=len(fields) + 1, column=0, sticky="w", padx=5, pady=5)
        recurring = ctk.CTkEntry(new_window)
        recurring.grid(row=len(fields) + 1, column=1, padx=5, pady=5)
        entries["recurring"] = recurring

        def save_new_task():
            task = {key: entry.get() for key, entry in entries.items()}
            task["completed"] = False
            task["recurring"] = int(entries["recurring"].get()) if entries["recurring"].get().isdigit() else 0

            if not validate_date(task["deadline"]):
                messagebox.showerror("Error", "Invalid deadline format. Use YYYY-MM-DD.")
                return

            self.tasks.append(task)
            save_tasks(self.tasks)
            self.refresh_task_list()
            new_window.destroy()

        save_button = ctk.CTkButton(new_window, text="Save Task", command=save_new_task)
        save_button.grid(row=len(fields) + 2, columnspan=2, pady=10)

    def delete_task(self):
        selected_task = simpledialog.askstring("Delete Task", "Enter task name to delete:")
        if not selected_task:
            return

        self.tasks = [task for task in self.tasks if task["name"].lower() != selected_task.lower()]
        save_tasks(self.tasks)
        self.refresh_task_list()

    def mark_complete(self):
        selected_task = simpledialog.askstring("Mark Complete", "Enter task name to mark as completed:")
        if not selected_task:
            return

        for task in self.tasks:
            if task["name"].lower() == selected_task.lower():
                task["completed"] = True
                break

        save_tasks(self.tasks)
        self.refresh_task_list()

    def search_tasks(self):
        query = self.search_var.get().lower()
        results = [task for task in self.tasks if query in task["name"].lower() or query in task["category"].lower()]

        self.scrollable_frame.destroy()
        self.scrollable_frame = ctk.CTkScrollableFrame(self.task_frame)
        self.scrollable_frame.pack(fill="both", expand=True)

        for task in results:
            task_frame = ctk.CTkFrame(self.scrollable_frame)
            task_frame.pack(fill="x", pady=5)

            task_label = ctk.CTkLabel(task_frame, text=f"{task['name']} - {task['category']} - {task['deadline']}", anchor="w", width=300)
            task_label.pack(side="left", padx=5)

            task_status = "✓" if task['completed'] else "✗"
            status_label = ctk.CTkLabel(task_frame, text=f"Completed: {task_status}", anchor="w")
            status_label.pack(side="left", padx=5)

            priority_label = ctk.CTkLabel(task_frame, text=f"Priority: {task['priority']}", anchor="w")
            priority_label.pack(side="left", padx=5)

    def filter_tasks(self):
        category = simpledialog.askstring("Filter", "Enter category:")
        if not category:
            return

        filtered = [task for task in self.tasks if task["category"].lower() == category.lower()]
        self.scrollable_frame.destroy()
        self.scrollable_frame = ctk.CTkScrollableFrame(self.task_frame)
        self.scrollable_frame.pack(fill="both", expand=True)

        for task in filtered:
            task_frame = ctk.CTkFrame(self.scrollable_frame)
            task_frame.pack(fill="x", pady=5)

            task_label = ctk.CTkLabel(task_frame, text=f"{task['name']} - {task['category']} - {task['deadline']}", anchor="w", width=300)
            task_label.pack(side="left", padx=5)

            task_status = "✓" if task['completed'] else "✗"
            status_label = ctk.CTkLabel(task_frame, text=f"Completed: {task_status}", anchor="w")
            status_label.pack(side="left", padx=5)

            priority_label = ctk.CTkLabel(task_frame, text=f"Priority: {task['priority']}", anchor="w")
            priority_label.pack(side="left", padx=5)


if __name__ == "__main__":
    root = ctk.CTk()
    app = ToDoApp(root)
    root.mainloop()
