import tkinter as tk
from tkinter import messagebox
from backend.auth.auth import register_user, login_user
from gui.screens.dashboard import Dashboard


class LoginScreen(tk.Frame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent)
        self.parent = parent
        self.on_login_success = on_login_success
        self.is_signup = False
        self.parent.geometry("400x400")

        self.pack(fill="both", expand=True)

        # Header
        self.header_label = tk.Label(self, text="Login", font=("Helvetica", 16, "bold"))
        self.header_label.pack(pady=10)

        # Main form
        form = tk.Frame(self)
        form.pack(pady=5)

        tk.Label(form, text="Username:").grid(row=0, column=0, sticky="e")
        self.username_var = tk.StringVar()
        tk.Entry(form, textvariable=self.username_var).grid(row=0, column=1)

        tk.Label(form, text="Password:").grid(row=1, column=0, sticky="e")
        self.password_var = tk.StringVar()
        tk.Entry(form, textvariable=self.password_var, show="*").grid(row=1, column=1)

        # Signup fields
        self.extra_frame = tk.Frame(self)

        height_frame = tk.Frame(self.extra_frame)
        height_frame.pack()
        tk.Label(height_frame, text="Height:").pack(side="left")
        self.height_ft_var = tk.StringVar()
        self.height_in_var = tk.StringVar()
        tk.Entry(height_frame, textvariable=self.height_ft_var, width=3).pack(side="left")
        tk.Label(height_frame, text="ft").pack(side="left")
        tk.Entry(height_frame, textvariable=self.height_in_var, width=3).pack(side="left")
        tk.Label(height_frame, text="in").pack(side="left")

        weight_frame = tk.Frame(self.extra_frame)
        weight_frame.pack()
        tk.Label(weight_frame, text="Weight (lbs):").pack(side="left")
        self.weight_lbs_var = tk.StringVar()
        tk.Entry(weight_frame, textvariable=self.weight_lbs_var, width=6).pack(side="left")

        gender_frame = tk.Frame(self.extra_frame)
        gender_frame.pack()
        tk.Label(gender_frame, text="Gender (optional):").pack(side="left")
        self.gender_var = tk.StringVar()
        tk.Entry(gender_frame, textvariable=self.gender_var, width=10).pack(side="left")

        # Buttons
        self.action_button = tk.Button(self, text="Login", command=self.handle_action)
        self.action_button.pack(pady=10)

        self.toggle_button = tk.Button(self, text="Sign Up Instead", command=self.toggle_mode)
        self.toggle_button.pack()

    # ---------------- Mode toggle ----------------

    def toggle_mode(self):
        self.is_signup = not self.is_signup
        if self.is_signup:
            self.header_label.config(text="Sign Up")
            self.action_button.config(text="Sign Up")
            self.toggle_button.config(text="Back to Login")
            self.extra_frame.pack(pady=5)
        else:
            self.header_label.config(text="Login")
            self.action_button.config(text="Login")
            self.toggle_button.config(text="Sign Up Instead")
            self.extra_frame.pack_forget()

    # ---------------- Main action ----------------

    def handle_action(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            messagebox.showerror("Missing info", "Username and password are required.")
            return

        if self.is_signup:
            self.handle_signup(username, password)
        else:
            self.handle_login(username, password)

    # ---------------- Signup ----------------

    def handle_signup(self, username, password):
        try:
            ft = int(self.height_ft_var.get() or 0)
            inch = int(self.height_in_var.get() or 0)
            height_cm = (ft * 12 + inch) * 2.54
        except ValueError:
            messagebox.showerror("Invalid height", "Height must be numbers.")
            return

        try:
            lbs = float(self.weight_lbs_var.get()) if self.weight_lbs_var.get() else None
            weight_kg = lbs * 0.453592 if lbs else None
        except ValueError:
            messagebox.showerror("Invalid weight", "Weight must be a number.")
            return

        gender = self.gender_var.get().strip() or None

        if register_user(username, password, height_cm=height_cm, weight_kg=weight_kg, gender=gender):
            messagebox.showinfo("Success", "Account created. You can now log in.")
            self.toggle_mode()

    # ---------------- Login ----------------

    def handle_action(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            messagebox.showerror("Missing info", "Username and password are required.")
            return

        if self.is_signup:
            # Height
            try:
                ft = int(self.height_ft_var.get()) if self.height_ft_var.get() else 0
                inch = int(self.height_in_var.get()) if self.height_in_var.get() else 0
                height_cm = (ft * 12 + inch) * 2.54
            except ValueError:
                messagebox.showerror("Invalid input", "Height must be numbers.")
                return

            # Weight
            try:
                lbs = float(self.weight_lbs_var.get()) if self.weight_lbs_var.get() else None
                weight_kg = lbs * 0.453592 if lbs else None
            except ValueError:
                messagebox.showerror("Invalid input", "Weight must be a number.")
                return

            gender = self.gender_var.get().strip() or None

            success = register_user(username, password, height_cm=height_cm, weight_kg=weight_kg, gender=gender)
            if success:
                messagebox.showinfo("Success", f"User '{username}' registered. You can now log in.")
                self.toggle_mode()
            return

        # LOGIN
        user = login_user(username, password)
        if user:
            self.destroy()
            Dashboard(self.parent, user)
        else:
            messagebox.showerror("Login failed", "Invalid username or password.")

