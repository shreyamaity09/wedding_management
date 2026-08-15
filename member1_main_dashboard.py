# ============================================================
# MEMBER 1 - LOGIN, REGISTRATION & MAIN DASHBOARD INTEGRATION
# Wedding Management System
# Python + Tkinter + MongoDB + PyMongo
# ============================================================

from tkinter import font as tkFont
DEFAULT_FONT = ("Helvetica", 10)
import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Import individual member modules (Ensure filenames match your project)
try:
    from member2_guests import GuestModule
except ImportError:
    GuestModule = None

try:
    from member3_vendors import VendorModule
except ImportError:
    VendorModule = None

try:
    from member4_venues_events import VenueModule, EventModule
except ImportError:
    VenueModule, EventModule = None, None

try:
    from member5_budget_reports import BudgetReportsModule
except ImportError:
    BudgetReportsModule = None


# ============================================================
# DATABASE CONNECTION SETUP
# ============================================================

def get_database():
    try:
        # Replace with your MongoDB connection string if using MongoDB Atlas
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        # Test connection
        client.admin.command('ping')
        print("Connected successfully to MongoDB!")
        return client["wedding_db"]
    except ConnectionFailure:
        print("Error: Could not connect to MongoDB. Ensure your MongoDB service is running.")
        return None

# Export database instance
db = get_database()
users_col = db["users"] if db is not None else None


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def hash_password(password):
    """Encrypts raw passwords using SHA-256 for secure DB storage."""
    return hashlib.sha256(password.encode()).hexdigest()


# ============================================================
# LOGIN & REGISTRATION WINDOW
# ============================================================

class LoginWindow(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Wedding Management System - Authentication")
        self.geometry("400x480")
        self.configure(bg="#ffffff")
        self.resizable(False, False)

        # Header Title
        tk.Label(
            self, text="💍 Wedding System", font=("Helvetica", 18, "bold"),
            bg="#ffffff", fg="#2c3e50"
        ).pack(pady=(25, 5))

        tk.Label(
            self, text="Please log in to manage your wedding events",
            font=("Helvetica", 9), bg="#ffffff", fg="#7f8c8d"
        ).pack(pady=(0, 20))

        # Input Frame
        frame = tk.Frame(self, bg="#ffffff", padx=20, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Username:", font=("Helvetica", 10, "bold"), bg="#ffffff").pack(anchor="w")
        self.ent_user = tk.Entry(frame, font=("Helvetica", 11), width=30)
        self.ent_user.pack(pady=(2, 12))

        tk.Label(frame, text="Password:", font=("Helvetica", 10, "bold"), bg="#ffffff").pack(anchor="w")
        self.ent_pass = tk.Entry(frame, font=("Helvetica", 11), show="•", width=30)
        self.ent_pass.pack(pady=(2, 20))

        # Buttons
        tk.Button(
            frame, text="Login", command=self.login,
            bg="#2ecc71", fg="white", font=("Helvetica", 10, "bold"),
            width=25, height=1, relief=tk.FLAT, cursor="hand2"
        ).pack(pady=5)

        tk.Button(
            frame, text="Register New Account", command=self.register,
            bg="#3498db", fg="white", font=("Helvetica", 10, "bold"),
            width=25, height=1, relief=tk.FLAT, cursor="hand2"
        ).pack(pady=5)

    def login(self):
        username = self.ent_user.get().strip()
        password = self.ent_pass.get().strip()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password!")
            return

        if users_col is None:
            messagebox.showerror("Database Error", "Database connection failed!")
            return

        hashed_pwd = hash_password(password)
        user = users_col.find_one({"username": username, "password": hashed_pwd})

        if user:
            messagebox.showinfo("Success", f"Welcome back, {username}!")
            self.destroy()  # Close login window
            app = MainDashboardApp(username)
            app.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def register(self):
        username = self.ent_user.get().strip()
        password = self.ent_pass.get().strip()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please provide a username and password to register!")
            return

        if users_col is None:
            messagebox.showerror("Database Error", "Database connection failed!")
            return

        if users_col.find_one({"username": username}):
            messagebox.showwarning("User Exists", "This username is already registered. Please login.")
            return

        users_col.insert_one({
            "username": username,
            "password": hash_password(password)
        })
        messagebox.showinfo("Success", "Account created successfully! You can now log in.")


# ============================================================
# MAIN DASHBOARD CONTROLLER (TABBED GUI INTEGRATION)
# ============================================================

class MainDashboardApp(tk.Tk):

    def __init__(self, username):
        super().__init__()
        self.title(f"Wedding Management System - Logged in as: {username}")
        self.geometry("940x550")
        self.configure(bg="#ecf0f1")

        # Top Navigation Bar
        top_bar = tk.Frame(self, bg="#2c3e50", height=50, padx=15)
        top_bar.pack(side=tk.TOP, fill=tk.X)

        tk.Label(
            top_bar, text="💍 Wedding Management Dashboard",
            font=("Helvetica", 14, "bold"), bg="#2c3e50", fg="#ffffff"
        ).pack(side=tk.LEFT, pady=10)

        tk.Button(
            top_bar, text="Logout", command=self.logout,
            bg="#e74c3c", fg="white", font=("Helvetica", 9, "bold"),
            padx=10, relief=tk.FLAT, cursor="hand2"
        ).pack(side=tk.RIGHT, pady=10)

        # Tabbed Notebook Control (Combines Member Modules)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- MEMBER 2: GUESTS TAB ---
        if GuestModule:
            self.guest_tab = GuestModule(self.notebook)
            self.notebook.add(self.guest_tab, text=" Guests Management ")
        else:
            self.add_placeholder_tab(" Guests Management (member2_guest.py missing)")

        # --- MEMBER 3: VENDORS TAB ---
        if VendorModule:
            self.vendor_tab = VendorModule(self.notebook)
            self.notebook.add(self.vendor_tab, text=" Vendors Management ")
        else:
            self.add_placeholder_tab(" Vendors Management (member3_vendor.py missing)")

        # --- MEMBER 4: VENUES TAB ---
        if VenueModule:
            self.venue_tab = VenueModule(self.notebook)
            self.notebook.add(self.venue_tab, text=" Venue Management ")
        else:
            self.add_placeholder_tab(" Venue Management (member4_venueevent.py missing)")

        # --- MEMBER 4: EVENTS TAB ---
        if EventModule:
            self.event_tab = EventModule(self.notebook)
            self.notebook.add(self.event_tab, text=" Event Management ")
        else:
            self.add_placeholder_tab(" Event Management (member4_venueevent.py missing)")

        # --- MEMBER 5: BUDGET & REPORTS TAB ---
        if BudgetReportsModule:
            self.budget_tab = BudgetReportsModule(self.notebook)
            self.notebook.add(self.budget_tab, text=" Budget & Reports ")
        else:
            self.add_placeholder_tab(" Budget & Reports (member5_budget_reports.py missing)")

    def add_placeholder_tab(self, tab_title):
        """Displays a missing module placeholder if a team member's file isn't found."""
        frame = tk.Frame(self.notebook, bg="#ffffff")
        tk.Label(
            frame, text=f"Module Not Found:\n{tab_title}",
            font=("Helvetica", 12, "italic"), bg="#ffffff", fg="#95a5a6"
        ).pack(expand=True)
        self.notebook.add(frame, text=tab_title.split(" ")[0])

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            self.destroy()
            login_app = LoginWindow()
            login_app.mainloop()


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()