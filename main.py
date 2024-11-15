import json
import os, platform

# File to save tasks
TASKS_FILE = "tasks.json"

# Load tasks from file
def load_tasks():
    try:
        with open(TASKS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Save tasks to file
def save_tasks(tasks):
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=4)

# Add a new task
def add_task(tasks):
    os.system('cls')
    task_name = input("Task Name: ")
    deadline = input("Deadline (YYYY-MM-DD): ")
    category = input("Category: ")
    priority = input("Priority (High/Medium/Low): ").capitalize()
    tasks.append({"name": task_name, "deadline": deadline, "category": category, "priority": priority, "completed": False})
    print("Task added successfully!")

# View all tasks
def view_tasks(tasks):
    os.system('cls')
    if not tasks:
        print("No tasks available!")
        return
    for idx, task in enumerate(tasks, start=1):
        status = "✓" if task["completed"] else "✗"
        print(f"{idx}. {task['name']} (Deadline: {task['deadline']}, Priority: {task['priority']}, Completed: {status})")

# Mark a task as completed
def complete_task(tasks):
    view_tasks(tasks)
    os.system('cls')
    try:
        idx = int(input("Enter task number to mark as complete: ")) - 1
        tasks[idx]["completed"] = True
        print("Task marked as complete!")
    except (IndexError, ValueError):
        print("Invalid task number.")

# Delete a task
def delete_task(tasks):
    os.system('cls')
    view_tasks(tasks)
    try:
        idx = int(input("Enter task number to delete: ")) - 1
        tasks.pop(idx)
        print("Task deleted successfully!")
    except (IndexError, ValueError):
        print("Invalid task number.")

# Main menu
def main():
    os.system('cls')
    tasks = load_tasks()
    while True:
        print("\nTo-Do List Menu:")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Complete Task")
        print("4. Delete Task")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            add_task(tasks)
        elif choice == "2":
            view_tasks(tasks)
        elif choice == "3":
            complete_task(tasks)
        elif choice == "4":
            delete_task(tasks)
        elif choice == "5":
            save_tasks(tasks)
            print("Goodbye!")
            break
        else:
            os.system('cls')
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
