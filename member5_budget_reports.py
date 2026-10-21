
import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from datetime import datetime


class BudgetReportsModule(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg="#ecf0f1")

        self.client = None
        self.budgets_col = None
        self.selected_id = None

        self.connect_database()
        self.create_widgets()
        self.load_budgets()

    def connect_database(self):
        try:
            self.client = MongoClient(
                "mongodb://localhost:27017/",
                serverSelectionTimeoutMS=2000
            )
            self.client.admin.command("ping")
            self.budgets_col = self.client["wedding_db"]["budgets"]

        except PyMongoError as error:
            self.budgets_col = None
            messagebox.showerror(
                "Database Error",
                f"Could not connect to MongoDB.\n{error}"
            )

    def create_widgets(self):
        tk.Label(
            self,
            text="Budget Management",
            font=("Helvetica", 18, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        ).pack(pady=12)

        form = tk.Frame(self, bg="#ecf0f1")
        form.pack(fill="x", padx=20, pady=5)

        tk.Label(form, text="Category:", bg="#ecf0f1").grid(
            row=0, column=0, sticky="w", padx=5, pady=6
        )
        self.category_entry = tk.Entry(form, width=25)
        self.category_entry.grid(row=0, column=1, padx=5, pady=6)

        tk.Label(form, text="Estimated Amount:", bg="#ecf0f1").grid(
            row=1, column=0, sticky="w", padx=5, pady=6
        )
        self.estimated_entry = tk.Entry(form, width=25)
        self.estimated_entry.grid(row=1, column=1, padx=5, pady=6)

        tk.Label(form, text="Actual Amount:", bg="#ecf0f1").grid(
            row=2, column=0, sticky="w", padx=5, pady=6
        )
        self.actual_entry = tk.Entry(form, width=25)
        self.actual_entry.grid(row=2, column=1, padx=5, pady=6)

        tk.Label(form, text="Notes:", bg="#ecf0f1").grid(
            row=3, column=0, sticky="w", padx=5, pady=6
        )
        self.notes_entry = tk.Entry(form, width=25)
        self.notes_entry.grid(row=3, column=1, padx=5, pady=6)

        buttons = tk.Frame(self, bg="#ecf0f1")
        buttons.pack(pady=8)

        tk.Button(
            buttons, text="Add Budget", command=self.add_budget,
            bg="#27ae60", fg="white", width=13
        ).grid(row=0, column=0, padx=4)

        tk.Button(
            buttons, text="Update Selected", command=self.update_budget,
            bg="#2980b9", fg="white", width=14
        ).grid(row=0, column=1, padx=4)

        tk.Button(
            buttons, text="Delete Selected", command=self.delete_budget,
            bg="#c0392b", fg="white", width=14
        ).grid(row=0, column=2, padx=4)

        tk.Button(
            buttons, text="Clear", command=self.clear_form,
            width=10
        ).grid(row=0, column=3, padx=4)

        columns = ("category", "estimated", "actual", "difference", "notes")

        self.tree = ttk.Treeview(
            self, columns=columns, show="headings", height=10
        )

        headings = {
            "category": "Category",
            "estimated": "Estimated Amount",
            "actual": "Actual Amount",
            "difference": "Remaining",
            "notes": "Notes"
        }

        for column, heading in headings.items():
            self.tree.heading(column, text=heading)

        self.tree.column("category", width=150)
        self.tree.column("estimated", width=130, anchor="e")
        self.tree.column("actual", width=130, anchor="e")
        self.tree.column("difference", width=120, anchor="e")
        self.tree.column("notes", width=220)

        self.tree.pack(fill="both", expand=True, padx=15, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.select_budget)

        self.summary_label = tk.Label(
            self,
            text="Estimated Total: 0.00 | Actual Total: 0.00",
            font=("Helvetica", 11, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        self.summary_label.pack(pady=8)

    def get_form_data(self):
        category = self.category_entry.get().strip()
        estimated_text = self.estimated_entry.get().strip()
        actual_text = self.actual_entry.get().strip()
        notes = self.notes_entry.get().strip()

        if not category or not estimated_text or not actual_text:
            messagebox.showwarning(
                "Missing Information",
                "Enter a category, estimated amount and actual amount."
            )
            return None

        try:
            estimated = float(estimated_text)
            actual = float(actual_text)

            if estimated < 0 or actual < 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid Amount",
                "Amounts must be valid non-negative numbers."
            )
            return None

        return {
            "category": category,
            "estimated": estimated,
            "actual": actual,
            "notes": notes
        }

    def add_budget(self):
        if self.budgets_col is None:
            messagebox.showerror("Database Error", "MongoDB is unavailable.")
            return

        data = self.get_form_data()
        if data is None:
            return

        data["created_at"] = datetime.now().isoformat()

        try:
            self.budgets_col.insert_one(data)
            self.load_budgets()
            self.clear_form()
            messagebox.showinfo("Success", "Budget added successfully.")

        except PyMongoError as error:
            messagebox.showerror("Database Error", str(error))

    def load_budgets(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if self.budgets_col is None:
            self.update_summary(0, 0)
            return

        estimated_total = 0.0
        actual_total = 0.0

        try:
            for budget in self.budgets_col.find().sort("created_at", -1):
                estimated = float(budget.get("estimated", 0))
                actual = float(budget.get("actual", 0))

                estimated_total += estimated
                actual_total += actual

                self.tree.insert(
                    "",
                    "end",
                    iid=str(budget["_id"]),
                    values=(
                        budget.get("category", ""),
                        f"{estimated:.2f}",
                        f"{actual:.2f}",
                        f"{estimated - actual:.2f}",
                        budget.get("notes", "")
                    )
                )

            self.update_summary(estimated_total, actual_total)

        except PyMongoError as error:
            messagebox.showerror("Database Error", str(error))

    def select_budget(self, event=None):
        selection = self.tree.selection()

        if not selection:
            return

        self.selected_id = selection[0]
        values = self.tree.item(self.selected_id, "values")

        self.category_entry.delete(0, tk.END)
        self.category_entry.insert(0, values[0])

        self.estimated_entry.delete(0, tk.END)
        self.estimated_entry.insert(0, values[1])

        self.actual_entry.delete(0, tk.END)
        self.actual_entry.insert(0, values[2])

        self.notes_entry.delete(0, tk.END)
        self.notes_entry.insert(0, values[4])

    def update_budget(self):
        if self.budgets_col is None:
            messagebox.showerror("Database Error", "MongoDB is unavailable.")
            return

        if not self.selected_id:
            messagebox.showwarning(
                "Select Budget", "Select a budget row to update."
            )
            return

        data = self.get_form_data()
        if data is None:
            return

        try:
            from bson import ObjectId

            self.budgets_col.update_one(
                {"_id": ObjectId(self.selected_id)},
                {"$set": data}
            )

            self.load_budgets()
            self.clear_form()
            messagebox.showinfo("Success", "Budget updated successfully.")

        except (PyMongoError, ValueError) as error:
            messagebox.showerror("Update Error", str(error))

    def delete_budget(self):
        if self.budgets_col is None:
            messagebox.showerror("Database Error", "MongoDB is unavailable.")
            return

        if not self.selected_id:
            messagebox.showwarning(
                "Select Budget", "Select a budget row to delete."
            )
            return

        if not messagebox.askyesno(
            "Confirm Delete", "Delete the selected budget?"
        ):
            return

        try:
            from bson import ObjectId

            self.budgets_col.delete_one(
                {"_id": ObjectId(self.selected_id)}
            )

            self.load_budgets()
            self.clear_form()
            messagebox.showinfo("Success", "Budget deleted successfully.")

        except (PyMongoError, ValueError) as error:
            messagebox.showerror("Delete Error", str(error))

    def clear_form(self):
        self.category_entry.delete(0, tk.END)
        self.estimated_entry.delete(0, tk.END)
        self.actual_entry.delete(0, tk.END)
        self.notes_entry.delete(0, tk.END)

        self.selected_id = None

        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def update_summary(self, estimated_total, actual_total):
        remaining = estimated_total - actual_total

        self.summary_label.config(
            text=(
                f"Estimated Total: {estimated_total:.2f} | "
                f"Actual Total: {actual_total:.2f} | "
                f"Remaining: {remaining:.2f}"
            )
        )
