import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime, timedelta

TASKS_FILE = "tasks_v2.json"


# Utility functions for task management
def load_tasks():
    """Load tasks from a file."""
    try:
        with open(TASKS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_tasks(tasks):
    """Save tasks to a file."""
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=4)


def validate_date(date_str):
    """Validate a date in YYYY-MM-DD format."""
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

        # Apply styling
        self.style = ttk.Style()
        self.apply_light_mode()

        # Main UI Layout
        self.create_toolbar()
        self.create_task_treeview()
        self.refresh_task_list()

    def create_toolbar(self):
        """Create the toolbar with buttons, search bar, and dark mode toggle."""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(toolbar, text="Add Task", command=self.add_task).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(toolbar, text="Delete Task", command=self.delete_task).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(toolbar, text="Mark Complete", command=self.mark_complete).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(toolbar, text="Filter", command=self.filter_tasks).pack(side=tk.LEFT, padx=5, pady=5)

        # Search bar
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.RIGHT, padx=5, pady=5)
        search_entry.insert(0, "Search...")
        search_entry.bind("<FocusIn>", lambda e: search_entry.delete(0, tk.END))
        search_entry.bind("<Return>", lambda e: self.search_tasks())

        ttk.Button(toolbar, text="Search", command=self.search_tasks).pack(side=tk.RIGHT, padx=5, pady=5)

        # Dark mode toggle
        ttk.Checkbutton(
            toolbar, text="Dark Mode", command=self.toggle_theme
        ).pack(side=tk.RIGHT, padx=5, pady=5)

    def create_task_treeview(self):
        """Create the Treeview widget to display tasks."""
        columns = ("Name", "Deadline", "Category", "Priority", "Completed")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")

        self.tree.heading("Priority", text="Priority (High/Med/Low)")
        self.tree.pack(fill=tk.BOTH, expand=True)

    def apply_light_mode(self):
        """Apply light mode styling."""
        self.theme = "light"
        self.style.theme_use("default")
        self.style.configure(".", background="white", foreground="black")

    def apply_dark_mode(self):
        """Apply dark mode styling."""
        self.theme = "dark"
        self.style.theme_use("clam")
        self.style.configure(".", background="#2E2E2E", foreground="white")
        self.tree.tag_configure("High", background="#660000", foreground="white")
        self.tree.tag_configure("Medium", background="#666600", foreground="black")
        self.tree.tag_configure("Low", background="#006600", foreground="white")

    def toggle_theme(self):
        """Toggle between light and dark modes."""
        if self.theme == "light":
            self.apply_dark_mode()
        else:
            self.apply_light_mode()

    def refresh_task_list(self):
        """Refresh the displayed tasks in the Treeview."""
        self.tree.delete(*self.tree.get_children())
        for task in self.tasks:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    task["name"],
                    task["deadline"],
                    task["category"],
                    task["priority"],
                    "✓" if task["completed"] else "✗",
                ),
                tags=(task["priority"]),
            )

    def add_task(self):
        """Open a dialog to add a new task."""
        new_window = tk.Toplevel(self.root)
        new_window.title("Add Task")

        # Input fields
        fields = [("Task Name", "name"), ("Deadline (YYYY-MM-DD)", "deadline"), ("Category", "category")]
        entries = {}

        for i, (label_text, key) in enumerate(fields):
            tk.Label(new_window, text=label_text).grid(row=i, column=0, sticky=tk.W)
            entry = tk.Entry(new_window)
            entry.grid(row=i, column=1)
            entries[key] = entry

        tk.Label(new_window, text="Priority:").grid(row=len(fields), column=0, sticky=tk.W)
        priority = ttk.Combobox(new_window, values=["High", "Medium", "Low"])
        priority.grid(row=len(fields), column=1)
        entries["priority"] = priority

        tk.Label(new_window, text="Recurring (Days):").grid(row=len(fields) + 1, column=0, sticky=tk.W)
        recurring = tk.Entry(new_window)
        recurring.grid(row=len(fields) + 1, column=1)
        entries["recurring"] = recurring

        def save_new_task():
            task = {key: entry.get() for key, entry in entries.items()}
            task["completed"] = False
            task["recurring"] = int(entries["recurring"].get()) if entries["recurring"].get().isdigit() else 0

            # Validation
            if not validate_date(task["deadline"]):
                messagebox.showerror("Error", "Invalid deadline format. Use YYYY-MM-DD.")
                return

            # Save task
            self.tasks.append(task)
            save_tasks(self.tasks)
            self.refresh_task_list()
            new_window.destroy()

        ttk.Button(new_window, text="Save Task", command=save_new_task).grid(row=len(fields) + 2, columnspan=2)

    def delete_task(self):
        """Delete the selected task."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No task selected.")
            return

        for item in selected:
            index = self.tree.index(item)
            del self.tasks[index]
        save_tasks(self.tasks)
        self.refresh_task_list()

    def mark_complete(self):
        """Mark the selected task as completed."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No task selected.")
            return

        for item in selected:
            index = self.tree.index(item)
            self.tasks[index]["completed"] = True
        save_tasks(self.tasks)
        self.refresh_task_list()

    def search_tasks(self):
        """Search for tasks by name or category."""
        query = self.search_var.get().lower()
        results = [task for task in self.tasks if query in task["name"].lower() or query in task["category"].lower()]

        self.tree.delete(*self.tree.get_children())
        for task in results:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    task["name"],
                    task["deadline"],
                    task["category"],
                    task["priority"],
                    "✓" if task["completed"] else "✗",
                ),
            )

    def filter_tasks(self):
        """Filter tasks by category."""
        category = tk.simpledialog.askstring("Filter", "Enter category:")
        if not category:
            return

        filtered = [task for task in self.tasks if task["category"].lower() == category.lower()]
        self.tree.delete(*self.tree.get_children())
        for task in filtered:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    task["name"],
                    task["deadline"],
                    task["category"],
                    task["priority"],
                    "✓" if task["completed"] else "✗",
                ),
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()
