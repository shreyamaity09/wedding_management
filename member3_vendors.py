import tkinter as tk
from tkinter import ttk, messagebox
from bson.objectid import ObjectId
from database import db

# Get collection from MongoDB connection
vendors_col = db["vendors"] if db is not None else None

class VendorModule(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#ffffff")
        self.selected_id = None

        # ----------------------------------
        # LEFT PANEL: Input Form
        # ----------------------------------
        form = tk.LabelFrame(self, text=" Vendor Details ", font=("Helvetica", 10, "bold"), bg="#ffffff", padx=10, pady=10)
        form.place(x=10, y=10, width=280, height=430)

        tk.Label(form, text="Vendor Name:", bg="#ffffff").pack(anchor="w")
        self.ent_name = tk.Entry(form, width=28)
        self.ent_name.pack(pady=2)

        tk.Label(form, text="Service Provided:", bg="#ffffff").pack(anchor="w", pady=(8, 0))
        self.cmb_service = ttk.Combobox(form, values=["Catering", "Photography", "Floral & Decor", "Music & DJ", "Venue", "Makeup & Styling"], state="readonly", width=25)
        self.cmb_service.current(0)
        self.cmb_service.pack(pady=2)

        tk.Label(form, text="Contract Cost ($):", bg="#ffffff").pack(anchor="w", pady=(8, 0))
        self.ent_cost = tk.Entry(form, width=28)
        self.ent_cost.pack(pady=2)

        tk.Label(form, text="Booking Status:", bg="#ffffff").pack(anchor="w", pady=(8, 0))
        self.cmb_status = ttk.Combobox(form, values=["Booked", "In Talks", "Completed", "Cancelled"], state="readonly", width=25)
        self.cmb_status.current(1)  # Default to "In Talks"
        self.cmb_status.pack(pady=2)

        # Action Buttons
        tk.Button(form, text="Add Vendor", command=self.add_item, bg="#2ecc71", fg="white", width=20, font=("Helvetica", 9, "bold")).pack(pady=(18, 4))
        tk.Button(form, text="Update Vendor", command=self.update_item, bg="#f39c12", fg="white", width=20, font=("Helvetica", 9, "bold")).pack(pady=4)
        tk.Button(form, text="Delete Vendor", command=self.delete_item, bg="#e74c3c", fg="white", width=20, font=("Helvetica", 9, "bold")).pack(pady=4)
        tk.Button(form, text="Clear Form", command=self.clear_data, bg="#95a5a6", fg="white", width=20).pack(pady=4)

        # ----------------------------------
        # RIGHT PANEL: Data Table (Treeview)
        # ----------------------------------
        table_frame = tk.Frame(self, bg="#ffffff")
        table_frame.place(x=300, y=10, width=520, height=430)

        scroll_y = tk.Scrollbar(table_frame, orient=tk.VERTICAL)
        self.tree = ttk.Treeview(table_frame, columns=("ID", "Name", "Service", "Cost", "Status"), show="headings", yscrollcommand=scroll_y.set)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_y.config(command=self.tree.yview)

        # Set Column Headers
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Vendor Name")
        self.tree.heading("Service", text="Service")
        self.tree.heading("Cost", text="Cost ($)")
        self.tree.heading("Status", text="Status")

        # Set Column Widths
        self.tree.column("ID", width=0, stretch=tk.NO)  # Hide Mongo ID
        self.tree.column("Name", width=140)
        self.tree.column("Service", width=120)
        self.tree.column("Cost", width=90)
        self.tree.column("Status", width=90)

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<ButtonRelease-1>", self.select_item)

        # Load records on startup
        self.load_data()

    # ----------------------------------
    # CRUD OPERATIONS
    # ----------------------------------

    # CREATE
    def add_item(self):
        name = self.ent_name.get().strip()
        service = self.cmb_service.get()
        cost = self.ent_cost.get().strip()
        status = self.cmb_status.get()

        if not name or not cost:
            messagebox.showwarning("Validation Error", "Vendor Name and Cost fields are required!")
            return

        doc = {"name": name, "service": service, "cost": cost, "status": status}

        if vendors_col is not None:
            vendors_col.insert_one(doc)
            messagebox.showinfo("Success", "Vendor added successfully!")
            self.clear_data()
        else:
            messagebox.showerror("Error", "Database connection not available.")

    # READ
    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        if vendors_col is None:
            return

        for v in vendors_col.find():
            self.tree.insert("", tk.END, values=(
                str(v["_id"]),
                v.get("name", ""),
                v.get("service", ""),
                v.get("cost", ""),
                v.get("status", "")
            ))

    # UPDATE
    def update_item(self):
        if not self.selected_id:
            messagebox.showwarning("Selection Error", "Please select a vendor from the table to update.")
            return

        updated_doc = {
            "name": self.ent_name.get().strip(),
            "service": self.cmb_service.get(),
            "cost": self.ent_cost.get().strip(),
            "status": self.cmb_status.get()
        }

        if vendors_col is not None:
            vendors_col.update_one({"_id": ObjectId(self.selected_id)}, {"$set": updated_doc})
            messagebox.showinfo("Success", "Vendor updated successfully!")
            self.clear_data()

    # DELETE
    def delete_item(self):
        if not self.selected_id:
            messagebox.showwarning("Selection Error", "Please select a vendor from the table to delete.")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this vendor?"):
            if vendors_col is not None:
                vendors_col.delete_one({"_id": ObjectId(self.selected_id)})
                messagebox.showinfo("Success", "Vendor deleted successfully!")
                self.clear_data()

    # SELECT ITEM FROM TABLE
    def select_item(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], "values")
            self.selected_id = values[0]

            self.ent_name.delete(0, tk.END)
            self.ent_name.insert(0, values[1])

            self.cmb_service.set(values[2])

            self.ent_cost.delete(0, tk.END)
            self.ent_cost.insert(0, values[3])

            self.cmb_status.set(values[4])

    # CLEAR FORM FIELDS
    def clear_data(self):
        self.selected_id = None
        self.ent_name.delete(0, tk.END)
        self.cmb_service.current(0)
        self.ent_cost.delete(0, tk.END)
        self.cmb_status.current(1)
        self.load_data()


# =======================================================
# STANDALONE RUN BLOCK (Run this file directly in VS Code)
# =======================================================
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Wedding System - Vendor Management Test")
    root.geometry("840x460")

    app = VendorModule(root)
    app.pack(fill=tk.BOTH, expand=True)

    root.mainloop()