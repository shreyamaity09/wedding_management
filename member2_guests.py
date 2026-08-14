import tkinter as tk
from tkinter import ttk, messagebox
from bson.objectid import ObjectId
from database import db

# Get collection from MongoDB connection
guests_col = db["guests"] if db is not None else None

class GuestModule(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#ffffff")
        self.selected_id = None

        # ----------------------------------
        # LEFT PANEL: Input Form
        # ----------------------------------
        form = tk.LabelFrame(self, text=" Guest Details ", font=("Helvetica", 10, "bold"), bg="#ffffff", padx=10, pady=10)
        form.place(x=10, y=10, width=280, height=430)

        tk.Label(form, text="Guest Name:", bg="#ffffff").pack(anchor="w")
        self.ent_name = tk.Entry(form, width=28)
        self.ent_name.pack(pady=2)

        tk.Label(form, text="Phone Number:", bg="#ffffff").pack(anchor="w", pady=(8, 0))
        self.ent_phone = tk.Entry(form, width=28)
        self.ent_phone.pack(pady=2)

        tk.Label(form, text="RSVP Status:", bg="#ffffff").pack(anchor="w", pady=(8, 0))
        self.cmb_status = ttk.Combobox(form, values=["Attending", "Declined", "Pending"], state="readonly", width=25)
        self.cmb_status.current(2)  # Default to "Pending"
        self.cmb_status.pack(pady=2)

        tk.Label(form, text="Dietary Preference:", bg="#ffffff").pack(anchor="w", pady=(8, 0))
        self.ent_diet = tk.Entry(form, width=28)
        self.ent_diet.pack(pady=2)

        # Action Buttons
        tk.Button(form, text="Add Guest", command=self.add_item, bg="#2ecc71", fg="white", width=20, font=("Helvetica", 9, "bold")).pack(pady=(18, 4))
        tk.Button(form, text="Update Guest", command=self.update_item, bg="#f39c12", fg="white", width=20, font=("Helvetica", 9, "bold")).pack(pady=4)
        tk.Button(form, text="Delete Guest", command=self.delete_item, bg="#e74c3c", fg="white", width=20, font=("Helvetica", 9, "bold")).pack(pady=4)
        tk.Button(form, text="Clear Form", command=self.clear_data, bg="#95a5a6", fg="white", width=20).pack(pady=4)

       # ----------------------------------
        # RIGHT PANEL: Data Table (Treeview)
        # ----------------------------------
        table_frame = tk.Frame(self, bg="#ffffff")
        table_frame.place(x=300, y=10, width=520, height=430)

        # 1. Create Both Scrollbars
        scroll_y = tk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scroll_x = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)

        # 2. Create Treeview with both x and y scroll commands
        self.tree = ttk.Treeview(
            table_frame, 
            columns=("ID", "Name", "Phone", "Status", "Diet"), 
            show="headings", 
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )

        # 3. Configure Scrollbar Targets
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        # 4. Pack Elements in Correct Order
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)         # Right Vertical Bar
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)        # Bottom Horizontal Bar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True) # Center Table

        # Set Column Headers
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Phone", text="Phone Number")
        self.tree.heading("Status", text="RSVP Status")
        self.tree.heading("Diet", text="Dietary Preference")

        # Set Larger Column Widths and DISABLE stretch so horizontal scroll activates
        self.tree.column("ID", width=0, stretch=tk.NO)        # Hidden Mongo ID
        self.tree.column("Name", width=180, stretch=tk.NO)
        self.tree.column("Phone", width=150, stretch=tk.NO)
        self.tree.column("Status", width=130, stretch=tk.NO)
        self.tree.column("Diet", width=220, stretch=tk.NO)    # Total width = 680px (> 520px frame)

        self.tree.bind("<ButtonRelease-1>", self.select_item)

        # Vertical Mouse Wheel Scroll Support
        def _on_mousewheel(event):
            if event.delta:
                self.tree.yview_scroll(int(-1 * (event.delta / 120)), "units")
            else:
                self.tree.yview_scroll(int(event.num == 5) - int(event.num == 4), "units")

        self.tree.bind("<MouseWheel>", _on_mousewheel)
        self.tree.bind("<Button-4>", _on_mousewheel)
        self.tree.bind("<Button-5>", _on_mousewheel)

    # ----------------------------------
    # CRUD OPERATIONS
    # ----------------------------------

    # CREATE
    def add_item(self):
        name = self.ent_name.get().strip()
        phone = self.ent_phone.get().strip()
        status = self.cmb_status.get()
        diet = self.ent_diet.get().strip()

        if not name or not phone:
            messagebox.showwarning("Validation Error", "Name and Phone fields are required!")
            return

        doc = {"name": name, "phone": phone, "status": status, "diet": diet}
        
        if guests_col is not None:
            guests_col.insert_one(doc)
            messagebox.showinfo("Success", "Guest added successfully!")
            self.clear_data()
        else:
            messagebox.showerror("Error", "Database connection not available.")

    # READ
    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        if guests_col is None:
            return

        for g in guests_col.find():
            self.tree.insert("", tk.END, values=(
                str(g["_id"]),
                g.get("name", ""),
                g.get("phone", ""),
                g.get("status", ""),
                g.get("diet", "")
            ))

    # UPDATE
    def update_item(self):
        if not self.selected_id:
            messagebox.showwarning("Selection Error", "Please select a guest from the table to update.")
            return

        updated_doc = {
            "name": self.ent_name.get().strip(),
            "phone": self.ent_phone.get().strip(),
            "status": self.cmb_status.get(),
            "diet": self.ent_diet.get().strip()
        }

        if guests_col is not None:
            guests_col.update_one({"_id": ObjectId(self.selected_id)}, {"$set": updated_doc})
            messagebox.showinfo("Success", "Guest updated successfully!")
            self.clear_data()

    # DELETE
    def delete_item(self):
        if not self.selected_id:
            messagebox.showwarning("Selection Error", "Please select a guest from the table to delete.")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this guest?"):
            if guests_col is not None:
                guests_col.delete_one({"_id": ObjectId(self.selected_id)})
                messagebox.showinfo("Success", "Guest deleted successfully!")
                self.clear_data()

    # SELECT ITEM FROM TABLE
    def select_item(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], "values")
            self.selected_id = values[0]

            self.ent_name.delete(0, tk.END)
            self.ent_name.insert(0, values[1])

            self.ent_phone.delete(0, tk.END)
            self.ent_phone.insert(0, values[2])

            self.cmb_status.set(values[3])

            self.ent_diet.delete(0, tk.END)
            self.ent_diet.insert(0, values[4])

    # CLEAR FORM FIELDS
    def clear_data(self):
        self.selected_id = None
        self.ent_name.delete(0, tk.END)
        self.ent_phone.delete(0, tk.END)
        self.cmb_status.current(2)
        self.ent_diet.delete(0, tk.END)
        self.load_data()


# =======================================================
# STANDALONE RUN BLOCK (Run this file directly in VS Code)
# =======================================================
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Wedding System - Guest Management Test")
    root.geometry("840x460")
    
    app = GuestModule(root)
    app.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()