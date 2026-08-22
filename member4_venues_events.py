# ============================================================
# MEMBER 4 - VENUE & EVENT MANAGEMENT
# Wedding Management System
# Python + Tkinter + MongoDB + PyMongo
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
from bson.objectid import ObjectId
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


# ============================================================
# DATABASE CONNECTION SETUP
# ============================================================

def get_database():
    try:
        client = MongoClient(
            "mongodb://localhost:27017/",
            serverSelectionTimeoutMS=2000
        )
        client.admin.command('ping')
        print("Connected successfully to MongoDB!")
        return client["wedding_db"]

    except ConnectionFailure:
        print(
            "Error: Could not connect to MongoDB. "
            "Ensure your MongoDB service is running."
        )
        return None


# Export database instance
db = get_database()

# Initialize collections
venues_col = db["venues"] if db is not None else None
events_col = db["events"] if db is not None else None


# ============================================================
# VENUE MANAGEMENT
# ============================================================

class VenueModule(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg="#ffffff")

        self.selected_id = None

        # -----------------------------
        # LEFT PANEL - Venue Form
        # -----------------------------

        form = tk.LabelFrame(
            self,
            text=" Venue Details ",
            font=("Helvetica", 10, "bold"),
            bg="#ffffff",
            padx=10,
            pady=10
        )
        form.place(x=10, y=10, width=280, height=430)

        tk.Label(
            form,
            text="Venue Name:",
            bg="#ffffff"
        ).pack(anchor="w")

        self.ent_name = tk.Entry(form, width=28)
        self.ent_name.pack(pady=2)

        tk.Label(
            form,
            text="Location:",
            bg="#ffffff"
        ).pack(anchor="w", pady=(8, 0))

        self.ent_location = tk.Entry(form, width=28)
        self.ent_location.pack(pady=2)

        tk.Label(
            form,
            text="Capacity:",
            bg="#ffffff"
        ).pack(anchor="w", pady=(8, 0))

        self.ent_capacity = tk.Entry(form, width=28)
        self.ent_capacity.pack(pady=2)

        tk.Label(
            form,
            text="Price:",
            bg="#ffffff"
        ).pack(anchor="w", pady=(8, 0))

        self.ent_price = tk.Entry(form, width=28)
        self.ent_price.pack(pady=2)

        tk.Label(
            form,
            text="Booking Status:",
            bg="#ffffff"
        ).pack(anchor="w", pady=(8, 0))

        self.cmb_status = ttk.Combobox(
            form,
            values=["Available", "Booked"],
            state="readonly",
            width=25
        )
        self.cmb_status.current(0)
        self.cmb_status.pack(pady=2)

        tk.Button(
            form,
            text="Add Venue",
            command=self.add_item,
            bg="#2ecc71",
            fg="white",
            width=20,
            font=("Helvetica", 9, "bold")
        ).pack(pady=(15, 4))

        tk.Button(
            form,
            text="Update Venue",
            command=self.update_item,
            bg="#f39c12",
            fg="white",
            width=20,
            font=("Helvetica", 9, "bold")
        ).pack(pady=4)

        tk.Button(
            form,
            text="Delete Venue",
            command=self.delete_item,
            bg="#e74c3c",
            fg="white",
            width=20,
            font=("Helvetica", 9, "bold")
        ).pack(pady=4)

        tk.Button(
            form,
            text="Clear Form",
            command=self.clear_data,
            bg="#95a5a6",
            fg="white",
            width=20,
            height=1,
            pady=0
        ).pack(pady=4)

        # -----------------------------
        # RIGHT PANEL - Venue Table
        # -----------------------------

        table_frame = tk.Frame(self, bg="#ffffff")
        table_frame.place(x=300, y=10, width=520, height=430)

        scroll_y = tk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=(
                "ID",
                "Name",
                "Location",
                "Capacity",
                "Price",
                "Status"
            ),
            show="headings",
            yscrollcommand=scroll_y.set
        )

        scroll_y.config(command=self.tree.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Venue Name")
        self.tree.heading("Location", text="Location")
        self.tree.heading("Capacity", text="Capacity")
        self.tree.heading("Price", text="Price")
        self.tree.heading("Status", text="Status")

        self.tree.column(
            "ID",
            width=0,
            stretch=tk.NO
        )
        self.tree.column(
            "Name",
            width=150,
            stretch=tk.NO
        )
        self.tree.column(
            "Location",
            width=110,
            stretch=tk.NO
        )
        self.tree.column(
            "Capacity",
            width=80,
            stretch=tk.NO
        )
        self.tree.column(
            "Price",
            width=100,
            stretch=tk.NO
        )
        self.tree.column(
            "Status",
            width=90,
            stretch=tk.NO
        )

        self.tree.pack(
            fill=tk.BOTH,
            expand=True
        )

        self.tree.bind(
            "<ButtonRelease-1>",
            self.select_item
        )

        self.load_data()

    # ========================================================
    # CREATE VENUE
    # ========================================================

    def add_item(self):
        name = self.ent_name.get().strip()
        location = self.ent_location.get().strip()
        capacity = self.ent_capacity.get().strip()
        price = self.ent_price.get().strip()
        status = self.cmb_status.get()

        if not name or not location or not capacity or not price:
            messagebox.showwarning(
                "Validation Error",
                "Venue Name, Location, Capacity and Price are required!"
            )
            return

        try:
            capacity = int(capacity)
            price = float(price)

        except ValueError:
            messagebox.showwarning(
                "Validation Error",
                "Capacity must be a number and Price must be numeric!"
            )
            return

        doc = {
            "venueName": name,
            "location": location,
            "capacity": capacity,
            "price": price,
            "availability": status == "Available",
            "bookingStatus": status
        }

        if venues_col is not None:
            venues_col.insert_one(doc)

            messagebox.showinfo(
                "Success",
                "Venue added successfully!"
            )

            self.clear_data()

        else:
            messagebox.showerror(
                "Error",
                "Database connection not available."
            )

    # ========================================================
    # READ VENUE
    # ========================================================

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        if venues_col is None:
            return

        for venue in venues_col.find():
            self.tree.insert(
                "",
                tk.END,
                values=(
                    str(venue["_id"]),
                    venue.get("venueName", ""),
                    venue.get("location", ""),
                    venue.get("capacity", ""),
                    venue.get("price", ""),
                    venue.get("bookingStatus", "")
                )
            )

    # ========================================================
    # UPDATE VENUE
    # ========================================================

    def update_item(self):
        if not self.selected_id:
            messagebox.showwarning(
                "Selection Error",
                "Please select a venue from the table to update."
            )
            return

        try:
            capacity = int(
                self.ent_capacity.get().strip()
            )
            price = float(
                self.ent_price.get().strip()
            )

        except ValueError:
            messagebox.showwarning(
                "Validation Error",
                "Capacity must be a number and Price must be numeric!"
            )
            return

        updated_doc = {
            "venueName": self.ent_name.get().strip(),
            "location": self.ent_location.get().strip(),
            "capacity": capacity,
            "price": price,
            "availability": self.cmb_status.get() == "Available",
            "bookingStatus": self.cmb_status.get()
        }

        if venues_col is not None:
            venues_col.update_one(
                {"_id": ObjectId(self.selected_id)},
                {"$set": updated_doc}
            )

            messagebox.showinfo(
                "Success",
                "Venue updated successfully!"
            )

            self.clear_data()

    # ========================================================
    # DELETE VENUE
    # ========================================================

    def delete_item(self):
        if not self.selected_id:
            messagebox.showwarning(
                "Selection Error",
                "Please select a venue from the table to delete."
            )
            return

        if messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this venue?"
        ):
            if venues_col is not None:
                venues_col.delete_one(
                    {"_id": ObjectId(self.selected_id)}
                )

                messagebox.showinfo(
                    "Success",
                    "Venue deleted successfully!"
                )

                self.clear_data()

    # ========================================================
    # SELECT VENUE
    # ========================================================

    def select_item(self, event):
        selected = self.tree.selection()

        if selected:
            values = self.tree.item(
                selected[0],
                "values"
            )

            self.selected_id = values[0]

            self.ent_name.delete(0, tk.END)
            self.ent_name.insert(0, values[1])

            self.ent_location.delete(0, tk.END)
            self.ent_location.insert(0, values[2])

            self.ent_capacity.delete(0, tk.END)
            self.ent_capacity.insert(0, values[3])

            self.ent_price.delete(0, tk.END)
            self.ent_price.insert(0, values[4])

            self.cmb_status.set(values[5])

    # ========================================================
    # CLEAR VENUE FORM
    # ========================================================

    def clear_data(self):
        self.selected_id = None

        self.ent_name.delete(0, tk.END)
        self.ent_location.delete(0, tk.END)
        self.ent_capacity.delete(0, tk.END)
        self.ent_price.delete(0, tk.END)

        self.cmb_status.current(0)

        self.load_data()


# ============================================================
# EVENT MANAGEMENT
# ============================================================

class EventModule(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg="#ffffff")

        self.selected_id = None

        # -----------------------------
        # LEFT PANEL - Event Form
        # -----------------------------

        form = tk.LabelFrame(
            self,
            text=" Event Details ",
            font=("Helvetica", 10, "bold"),
            bg="#ffffff",
            padx=10,
            pady=10
        )

        form.place(
            x=10,
            y=10,
            width=280,
            height=430
        )

        tk.Label(
            form,
            text="Function Name:",
            bg="#ffffff"
        ).pack(anchor="w")

        self.cmb_event = ttk.Combobox(
            form,
            values=[
                "Engagement",
                "Haldi",
                "Mehendi",
                "Sangeet",
                "Wedding Ceremony",
                "Reception"
            ],
            state="readonly",
            width=25
        )

        self.cmb_event.current(0)
        self.cmb_event.pack(pady=2)

        tk.Label(
            form,
            text="Date (DD-MM-YYYY):",
            bg="#ffffff"
        ).pack(
            anchor="w",
            pady=(8, 0)
        )

        self.ent_date = tk.Entry(
            form,
            width=28
        )
        self.ent_date.pack(pady=2)

        tk.Label(
            form,
            text="Time:",
            bg="#ffffff"
        ).pack(
            anchor="w",
            pady=(8, 0)
        )

        self.ent_time = tk.Entry(
            form,
            width=28
        )
        self.ent_time.pack(pady=2)

        tk.Label(
            form,
            text="Venue:",
            bg="#ffffff"
        ).pack(
            anchor="w",
            pady=(8, 0)
        )

        self.cmb_venue = ttk.Combobox(
            form,
            state="readonly",
            width=25
        )
        self.cmb_venue.pack(pady=2)

        tk.Label(
            form,
            text="Description:",
            bg="#ffffff"
        ).pack(
            anchor="w",
            pady=(8, 0)
        )

        self.ent_description = tk.Entry(
            form,
            width=28
        )
        self.ent_description.pack(pady=2)

        tk.Button(
            form,
            text="Add Event",
            command=self.add_item,
            bg="#2ecc71",
            fg="white",
            width=20,
            font=("Helvetica", 9, "bold")
        ).pack(pady=(15, 4))

        tk.Button(
            form,
            text="Update Event",
            command=self.update_item,
            bg="#f39c12",
            fg="white",
            width=20,
            font=("Helvetica", 9, "bold")
        ).pack(pady=4)

        tk.Button(
            form,
            text="Delete Event",
            command=self.delete_item,
            bg="#e74c3c",
            fg="white",
            width=20,
            font=("Helvetica", 9, "bold")
        ).pack(pady=4)

        tk.Button(
            form,
            text="Clear Form",
            command=self.clear_data,
            bg="#95a5a6",
            fg="white",
            width=20,
            height=1,
            pady=0
        ).pack(pady=4)

        tk.Button(
            form,
            text="Refresh Venues",
            command=self.refresh_venues,
            bg="#3498db",
            fg="white",
            width=20
        ).pack(pady=4)

        # -----------------------------
        # RIGHT PANEL - Event Table
        # -----------------------------

        table_frame = tk.Frame(
            self,
            bg="#ffffff"
        )

        table_frame.place(
            x=300,
            y=10,
            width=520,
            height=430
        )

        scroll_y = tk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL
        )

        scroll_x = tk.Scrollbar(
            table_frame,
            orient=tk.HORIZONTAL
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=(
                "ID",
                "Event",
                "Date",
                "Time",
                "Venue",
                "Description"
            ),
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )

        scroll_y.config(
            command=self.tree.yview
        )

        scroll_x.config(
            command=self.tree.xview
        )

        scroll_y.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )

        scroll_x.pack(
            side=tk.BOTTOM,
            fill=tk.X
        )

        self.tree.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )

        self.tree.heading(
            "ID",
            text="ID"
        )

        self.tree.heading(
            "Event",
            text="Function"
        )

        self.tree.heading(
            "Date",
            text="Date"
        )

        self.tree.heading(
            "Time",
            text="Time"
        )

        self.tree.heading(
            "Venue",
            text="Venue"
        )

        self.tree.heading(
            "Description",
            text="Description"
        )

        self.tree.column(
            "ID",
            width=0,
            stretch=tk.NO
        )

        self.tree.column(
            "Event",
            width=130,
            stretch=tk.NO
        )

        self.tree.column(
            "Date",
            width=100,
            stretch=tk.NO
        )

        self.tree.column(
            "Time",
            width=90,
            stretch=tk.NO
        )

        self.tree.column(
            "Venue",
            width=160,
            stretch=tk.NO
        )

        self.tree.column(
            "Description",
            width=280,
            stretch=tk.NO
        )

        self.tree.bind(
            "<ButtonRelease-1>",
            self.select_item
        )

        self.refresh_venues()
        self.load_data()

        # Refresh the venue list whenever the Event tab is selected
        self.bind(
            "<Visibility>",
            lambda event: self.refresh_venues()
        )

    # ========================================================
    # REFRESH VENUES
    # ========================================================

    def refresh_venues(self):
        if venues_col is None:
            self.cmb_venue["values"] = []
            return

        venue_names = [
            v.get("venueName", "")
            for v in venues_col.find(
                {},
                {"venueName": 1}
            )
            if v.get("venueName")
        ]

        self.cmb_venue["values"] = venue_names

        if venue_names:
            self.cmb_venue.current(0)
        else:
            self.cmb_venue.set("")

    # ========================================================
    # CREATE EVENT
    # ========================================================

    def add_item(self):
        event_name = self.cmb_event.get()
        date_text = self.ent_date.get().strip()
        time_text = self.ent_time.get().strip()
        venue_name = self.cmb_venue.get()
        description = self.ent_description.get().strip()

        if not date_text or not time_text or not venue_name:
            messagebox.showwarning(
                "Validation Error",
                "Date, Time and Venue are required!"
            )
            return

        try:
            event_date = datetime.strptime(
                date_text,
                "%d-%m-%Y"
            )

        except ValueError:
            messagebox.showwarning(
                "Validation Error",
                "Enter date in DD-MM-YYYY format."
            )
            return

        venue = (
            venues_col.find_one(
                {"venueName": venue_name}
            )
            if venues_col is not None
            else None
        )

        if venue is None:
            messagebox.showerror(
                "Error",
                "Selected venue not found."
            )
            return

        doc = {
            "eventName": event_name,
            "date": event_date,
            "time": time_text,
            "venue": venue["_id"],
            "description": description
        }

        if events_col is not None:
            events_col.insert_one(doc)

            messagebox.showinfo(
                "Success",
                "Event added successfully!"
            )

            self.clear_data()

        else:
            messagebox.showerror(
                "Error",
                "Database connection not available."
            )

    # ========================================================
    # READ EVENTS
    # ========================================================

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        if events_col is None:
            return

        for event in events_col.find().sort(
            "date",
            1
        ):

            venue = (
                venues_col.find_one(
                    {"_id": event.get("venue")}
                )
                if venues_col is not None
                else None
            )

            venue_name = (
                venue.get("venueName", "Unknown")
                if venue
                else "Unknown"
            )

            date_value = event.get("date")

            if isinstance(date_value, datetime):
                date_value = date_value.strftime(
                    "%d-%m-%Y"
                )

            self.tree.insert(
                "",
                tk.END,
                values=(
                    str(event["_id"]),
                    event.get("eventName", ""),
                    date_value,
                    event.get("time", ""),
                    venue_name,
                    event.get("description", "")
                )
            )

    # ========================================================
    # UPDATE EVENT
    # ========================================================

    def update_item(self):
        if not self.selected_id:
            messagebox.showwarning(
                "Selection Error",
                "Please select an event from the table to update."
            )
            return

        try:
            event_date = datetime.strptime(
                self.ent_date.get().strip(),
                "%d-%m-%Y"
            )

        except ValueError:
            messagebox.showwarning(
                "Validation Error",
                "Enter date in DD-MM-YYYY format."
            )
            return

        venue = (
            venues_col.find_one(
                {"venueName": self.cmb_venue.get()}
            )
            if venues_col is not None
            else None
        )

        if venue is None:
            messagebox.showerror(
                "Error",
                "Selected venue not found."
            )
            return

        updated_doc = {
            "eventName": self.cmb_event.get(),
            "date": event_date,
            "time": self.ent_time.get().strip(),
            "venue": venue["_id"],
            "description": self.ent_description.get().strip()
        }

        if events_col is not None:
            events_col.update_one(
                {"_id": ObjectId(self.selected_id)},
                {"$set": updated_doc}
            )

            messagebox.showinfo(
                "Success",
                "Event updated successfully!"
            )

            self.clear_data()

    # ========================================================
    # DELETE EVENT
    # ========================================================

    def delete_item(self):
        if not self.selected_id:
            messagebox.showwarning(
                "Selection Error",
                "Please select an event from the table to delete."
            )
            return

        if messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this event?"
        ):
            if events_col is not None:
                events_col.delete_one(
                    {"_id": ObjectId(self.selected_id)}
                )

                messagebox.showinfo(
                    "Success",
                    "Event deleted successfully!"
                )

                self.clear_data()

    # ========================================================
    # SELECT EVENT
    # ========================================================

    def select_item(self, event):
        selected = self.tree.selection()

        if selected:
            values = self.tree.item(
                selected[0],
                "values"
            )

            self.selected_id = values[0]

            self.cmb_event.set(values[1])

            self.ent_date.delete(
                0,
                tk.END
            )
            self.ent_date.insert(
                0,
                values[2]
            )

            self.ent_time.delete(
                0,
                tk.END
            )
            self.ent_time.insert(
                0,
                values[3]
            )

            self.cmb_venue.set(values[4])

            self.ent_description.delete(
                0,
                tk.END
            )
            self.ent_description.insert(
                0,
                values[5]
            )

    # ========================================================
    # CLEAR EVENT FORM
    # ========================================================

    def clear_data(self):
        self.selected_id = None

        self.cmb_event.current(0)

        self.ent_date.delete(
            0,
            tk.END
        )

        self.ent_time.delete(
            0,
            tk.END
        )

        self.ent_description.delete(
            0,
            tk.END
        )

        self.refresh_venues()

        if self.cmb_venue["values"]:
            self.cmb_venue.current(0)

        self.load_data()


# ============================================================
# STANDALONE RUN BLOCK
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    root.title(
        "Wedding System - Venue & Event Management"
    )

    root.geometry(
        "840x500"
    )

    notebook = ttk.Notebook(root)

    notebook.pack(
        fill=tk.BOTH,
        expand=True
    )

    venue_tab = VenueModule(notebook)
    event_tab = EventModule(notebook)

    notebook.add(
        venue_tab,
        text="Venue Management"
    )

    notebook.add(
        event_tab,
        text="Event Management"
    )

    root.mainloop()