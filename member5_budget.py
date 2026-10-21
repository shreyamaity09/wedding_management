# ============================================================
# MEMBER 5 - BUDGET & EXPENSE MANAGEMENT
# Wedding Management System
# Python + Tkinter + MongoDB + PyMongo
# UI style kept similar to the Guest Management screen
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
from bson.objectid import ObjectId
from datetime import datetime
from database import db

expenses_col = db["expenses"] if db is not None else None
budget_col = db["budget"] if db is not None else None


class BudgetReportsModule(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#ffffff")
        self.selected_id = None

        # Top panel: budget input and summary
        top_frame = tk.Frame(self, bg="#ecf0f1", padx=10, pady=8)
        top_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        tk.Label(
            top_frame, text="Total Budget (₹):",
            bg="#ecf0f1", font=("Helvetica", 9, "bold")
        ).grid(row=0, column=0, sticky="w", padx=5, pady=4)

        self.ent_total_budget = tk.Entry(top_frame, width=14)
        self.ent_total_budget.grid(row=0, column=1, padx=5, pady=4)

        tk.Button(
            top_frame, text="Set Budget", command=self.save_total_budget,
            bg="#2ecc71", fg="white", font=("Helvetica", 9, "bold"),
            relief=tk.FLAT, cursor="hand2"
        ).grid(row=0, column=2, padx=5, pady=4)

        self.lbl_alloc_budget = tk.Label(
            top_frame, text="Allocated: ₹0.00", bg="#3498db", fg="white",
            font=("Helvetica", 9, "bold"), padx=8, pady=6
        )
        self.lbl_alloc_budget.grid(row=0, column=3, padx=5, pady=4)

        self.lbl_spent = tk.Label(
            top_frame, text="Spent: ₹0.00", bg="#e67e22", fg="white",
            font=("Helvetica", 9, "bold"), padx=8, pady=6
        )
        self.lbl_spent.grid(row=0, column=4, padx=5, pady=4)

        self.lbl_remaining = tk.Label(
            top_frame, text="Remaining: ₹0.00", bg="#27ae60", fg="white",
            font=("Helvetica", 9, "bold"), padx=8, pady=6
        )
        self.lbl_remaining.grid(row=0, column=5, padx=5, pady=4)

        # Main content area, similar to Guest Management UI
        content = tk.Frame(self, bg="#ffffff")
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left panel: expense form
        form = tk.LabelFrame(
            content, text=" Expense Details ",
            font=("Helvetica", 10, "bold"), bg="#ffffff",
            padx=10, pady=10
        )
        form.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        form.configure(width=260)
        form.pack_propagate(False)

        tk.Label(form, text="Expense Category:", bg="#ffffff").pack(anchor="w")
        self.cmb_category = ttk.Combobox(
            form,
            values=[
                "Venue", "Catering", "Photography", "Decoration",
                "Attire & Makeup", "Entertainment", "Transport",
                "Miscellaneous"
            ],
            state="readonly", width=25
        )
        self.cmb_category.current(0)
        self.cmb_category.pack(fill=tk.X, pady=(2, 7))

        tk.Label(form, text="Description / Item:", bg="#ffffff").pack(anchor="w")
        self.ent_desc = tk.Entry(form)
        self.ent_desc.pack(fill=tk.X, pady=(2, 7))

        tk.Label(form, text="Estimated Amount (₹):", bg="#ffffff").pack(anchor="w")
        self.ent_estimated = tk.Entry(form)
        self.ent_estimated.pack(fill=tk.X, pady=(2, 7))

        tk.Label(form, text="Actual Amount Paid (₹):", bg="#ffffff").pack(anchor="w")
        self.ent_actual = tk.Entry(form)
        self.ent_actual.pack(fill=tk.X, pady=(2, 12))

        tk.Button(
            form, text="Add Expense", command=self.add_item,
            bg="#218c4a", fg="white", width=20,
            font=("Helvetica", 9, "bold"), relief=tk.FLAT, cursor="hand2"
        ).pack(fill=tk.X, pady=3)

        tk.Button(
            form, text="Update Expense", command=self.update_item,
            bg="#d99018", fg="white", width=20,
            font=("Helvetica", 9, "bold"), relief=tk.FLAT, cursor="hand2"
        ).pack(fill=tk.X, pady=3)

        tk.Button(
            form, text="Delete Expense", command=self.delete_item,
            bg="#c0392b", fg="white", width=20,
            font=("Helvetica", 9, "bold"), relief=tk.FLAT, cursor="hand2"
        ).pack(fill=tk.X, pady=3)

        tk.Button(
            form, text="Clear Form", command=self.clear_data,
            bg="#7f8c8d", fg="white", width=20,
            font=("Helvetica", 9, "bold"), relief=tk.FLAT, cursor="hand2"
        ).pack(fill=tk.X, pady=3)

        # Right panel: records table with scrollbars
        table_frame = tk.Frame(content, bg="#ffffff")
        table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Category", "Description", "Estimated", "Actual"),
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )

        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree.heading("ID", text="ID")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Estimated", text="Estimated (₹)")
        self.tree.heading("Actual", text="Actual Paid (₹)")

        # Hide the MongoDB ID but retain it for update/delete
        self.tree.column("ID", width=0, stretch=tk.NO)
        self.tree.column("Category", width=120, stretch=tk.NO)
        self.tree.column("Description", width=180, stretch=tk.NO)
        self.tree.column("Estimated", width=110, stretch=tk.NO)
        self.tree.column("Actual", width=120, stretch=tk.NO)

        self.tree.bind("<<TreeviewSelect>>", self.select_item)

        self.load_total_budget()
        self.load_data()

    def save_total_budget(self):
        value = self.ent_total_budget.get().strip()
        try:
            total = float(value)
            if total < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Validation Error", "Please enter a valid non-negative budget amount."
            )
            return

        if budget_col is None:
            messagebox.showerror("Database Error", "Database connection not available.")
            return

        budget_col.update_one(
            {}, {"$set": {"total_budget": total}}, upsert=True
        )
        messagebox.showinfo("Success", "Total budget saved successfully!")
        self.update_summary()

    def load_total_budget(self):
        if budget_col is not None:
            budget = budget_col.find_one()
            if budget and "total_budget" in budget:
                self.ent_total_budget.delete(0, tk.END)
                self.ent_total_budget.insert(0, str(budget["total_budget"]))

    def add_item(self):
        category = self.cmb_category.get()
        description = self.ent_desc.get().strip()
        estimated_text = self.ent_estimated.get().strip()
        actual_text = self.ent_actual.get().strip()

        if not description or not estimated_text:
            messagebox.showwarning(
                "Validation Error", "Description and Estimated Amount are required."
            )
            return

        try:
            estimated = float(estimated_text)
            actual = float(actual_text) if actual_text else 0.0
            if estimated < 0 or actual < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Validation Error", "Amounts must be valid non-negative numbers."
            )
            return

        if expenses_col is None:
            messagebox.showerror("Database Error", "Database connection not available.")
            return

        expenses_col.insert_one({
            "category": category,
            "description": description,
            "estimated": estimated,
            "actual": actual,
            "date_added": datetime.now()
        })
        messagebox.showinfo("Success", "Expense added successfully!")
        self.clear_data()

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        if expenses_col is not None:
            for expense in expenses_col.find().sort("date_added", -1):
                self.tree.insert(
                    "", tk.END,
                    values=(
                        str(expense["_id"]),
                        expense.get("category", ""),
                        expense.get("description", ""),
                        f'{float(expense.get("estimated", 0) or 0):,.2f}',
                        f'{float(expense.get("actual", 0) or 0):,.2f}'
                    )
                )

        self.update_summary()

    def update_item(self):
        if not self.selected_id:
            messagebox.showwarning(
                "Selection Error", "Please select an expense from the table to update."
            )
            return

        description = self.ent_desc.get().strip()
        if not description:
            messagebox.showwarning("Validation Error", "Description is required.")
            return

        try:
            estimated = float(self.ent_estimated.get().strip())
            actual_text = self.ent_actual.get().strip()
            actual = float(actual_text) if actual_text else 0.0
            if estimated < 0 or actual < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Validation Error", "Amounts must be valid non-negative numbers."
            )
            return

        if expenses_col is None:
            messagebox.showerror("Database Error", "Database connection not available.")
            return

        expenses_col.update_one(
            {"_id": ObjectId(self.selected_id)},
            {"$set": {
                "category": self.cmb_category.get(),
                "description": description,
                "estimated": estimated,
                "actual": actual
            }}
        )
        messagebox.showinfo("Success", "Expense updated successfully!")
        self.clear_data()

    def delete_item(self):
        if not self.selected_id:
            messagebox.showwarning(
                "Selection Error", "Please select an expense from the table to delete."
            )
            return

        if messagebox.askyesno(
            "Confirm Delete", "Are you sure you want to delete this expense?"
        ):
            if expenses_col is not None:
                expenses_col.delete_one({"_id": ObjectId(self.selected_id)})
                messagebox.showinfo("Success", "Expense deleted successfully!")
                self.clear_data()

    def select_item(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        self.selected_id = values[0]

        self.cmb_category.set(values[1])

        self.ent_desc.delete(0, tk.END)
        self.ent_desc.insert(0, values[2])

        self.ent_estimated.delete(0, tk.END)
        self.ent_estimated.insert(0, values[3].replace(",", ""))

        self.ent_actual.delete(0, tk.END)
        self.ent_actual.insert(0, values[4].replace(",", ""))

    def update_summary(self):
        total_budget = 0.0
        if budget_col is not None:
            budget = budget_col.find_one()
            if budget and "total_budget" in budget:
                total_budget = float(budget["total_budget"])

        total_spent = 0.0
        if expenses_col is not None:
            result = list(expenses_col.aggregate([
                {"$group": {"_id": None, "total": {"$sum": "$actual"}}}
            ]))
            if result:
                total_spent = float(result[0].get("total", 0) or 0)

        remaining = total_budget - total_spent
        self.lbl_alloc_budget.config(text=f"Allocated: ₹{total_budget:,.2f}")
        self.lbl_spent.config(text=f"Spent: ₹{total_spent:,.2f}")

        if remaining < 0:
            self.lbl_remaining.config(
                text=f"Over Budget: ₹{abs(remaining):,.2f}", bg="#e74c3c"
            )
        else:
            self.lbl_remaining.config(
                text=f"Remaining: ₹{remaining:,.2f}", bg="#27ae60"
            )

    def clear_data(self):
        self.selected_id = None
        self.cmb_category.current(0)
        self.ent_desc.delete(0, tk.END)
        self.ent_estimated.delete(0, tk.END)
        self.ent_actual.delete(0, tk.END)

        for selected in self.tree.selection():
            self.tree.selection_remove(selected)

        self.load_data()


# Run this file directly to test the module
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Wedding System - Budget & Expense Management")
    root.geometry("940x550")
    root.minsize(800, 480)

    app = BudgetReportsModule(root)
    app.pack(fill=tk.BOTH, expand=True)

    root.mainloop()
