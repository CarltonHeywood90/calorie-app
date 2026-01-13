import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import date
from backend.services.weight_service import (
    get_weight_history,
    log_weight,
    get_weight_logs_for_user,
    update_weight_log,
    delete_weight_log
)
from backend.db.connection import create_connection
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

BMI_CATEGORIES = [
    (0, 18.5, "Underweight"),
    (18.5, 24.9, "Normal"),
    (25, 29.9, "Overweight"),
    (30, 1000, "Obese")
]

class WeightEntryScreen(tk.Frame):
    def __init__(self, parent, user_id):
        super().__init__(parent)
        self.user_id = user_id

        # ---------- Configure grid ----------
        self.grid(sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(4, weight=1)  # Chart row expands
        self.rowconfigure(5, weight=1)  # Logs row expands

        # ---------- Header ----------
        tk.Label(self, text="Weight & BMI Tracker", font=("Helvetica", 16, "bold"))\
            .grid(row=0, column=0, columnspan=2, pady=10, sticky="w")

        # ---------- Weight Entry ----------
        entry_frame = tk.Frame(self)
        entry_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky="w")
        tk.Label(entry_frame, text="Weight (lb):").grid(row=0, column=0, padx=5)
        self.weight_var = tk.StringVar()
        tk.Entry(entry_frame, textvariable=self.weight_var, width=8).grid(row=0, column=1, padx=5)
        tk.Button(entry_frame, text="Log Weight", command=self.log_weight).grid(row=0, column=2, padx=5)

        # ---------- Current BMI ----------
        self.bmi_label = tk.Label(self, text="BMI: N/A", font=("Helvetica", 12, "bold"))
        self.bmi_label.grid(row=2, column=0, columnspan=2, pady=5, sticky="w")

        # ---------- Weight Logs Label ----------
        logs_label = tk.Label(self, text="Weight Logs:", font=("Helvetica", 12, "bold"))
        logs_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=(10,0))

        # ---------- Chart Frame ----------
        self.chart_frame = tk.Frame(self)
        self.chart_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=10)
        self.chart_frame.columnconfigure(0, weight=1)
        self.chart_frame.rowconfigure(0, weight=1)
        self.canvas = None

        # ---------- Weight Logs Frame ----------
        self.logs_frame = tk.Frame(self)
        self.logs_frame.grid(row=5, column=0, columnspan=2, sticky="nsew")
        self.logs_frame.columnconfigure(0, weight=1)

    # ------------------ Weight Logging ------------------
    def log_weight(self):
        try:
            weight_lb = float(self.weight_var.get())
            if weight_lb <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid weight", "Enter a number greater than 0.")
            return

        weight_kg = round(weight_lb * 0.453592, 2)
        log_weight(user_id=self.user_id, log_date=date.today(), weight_kg=weight_kg)
        messagebox.showinfo("Logged", f"Weight {weight_lb} lb logged for today.")
        self.weight_var.set("")
        self.update_daily_logs(date.today())

    # ------------------ Public API ------------------
    def update_daily_logs(self, log_date):
        self.refresh_bmi()
        self.refresh_chart()
        self.refresh_weight_logs()

    # ------------------ BMI ------------------
    def get_user_height_m(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT height_cm FROM users WHERE user_id = %s", (self.user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            return float(row[0]) / 100
        return 1.75

    def get_bmi_category(self, bmi):
        for lower, upper, cat in BMI_CATEGORIES:
            if lower <= bmi <= upper:
                return cat
        return "Unknown"

    def refresh_bmi(self):
        logs = get_weight_logs_for_user(self.user_id)
        if not logs:
            self.bmi_label.config(text="BMI: N/A")
            return
        latest_log = logs[-1]
        height_m = self.get_user_height_m()
        bmi = float(latest_log['weight_kg']) / (height_m ** 2)
        category = self.get_bmi_category(bmi)
        self.bmi_label.config(text=f"BMI: {bmi:.1f} ({category})")

    # ------------------ Chart ------------------
    def refresh_chart(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        logs = get_weight_logs_for_user(self.user_id)
        if not logs:
            return

        height_m = self.get_user_height_m()
        dates = [log['date'] for log in logs]
        weights_lb = [float(log['weight_kg']) / 0.453592 for log in logs]
        bmi_values = [float(log['weight_kg']) / (height_m ** 2) for log in logs]

        fig, ax1 = plt.subplots(figsize=(8,3), dpi=100)
        ax1.plot(dates, weights_lb, color='blue', marker='o', label='Weight (lb)')
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Weight (lb)", color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')

        ax2 = ax1.twinx()
        ax2.plot(dates, bmi_values, color='red', marker='x', linestyle='--', label='BMI')
        ax2.set_ylabel("BMI", color='red')
        ax2.tick_params(axis='y', labelcolor='red')

        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines + lines2, labels + labels2, loc='upper left')

        ax1.grid(True)
        fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

# ------------------ Weight Logs ------------------
    def refresh_weight_logs(self):
        # Clear previous log widgets
        for widget in self.logs_frame.winfo_children():
            widget.destroy()

        logs = get_weight_logs_for_user(self.user_id)
        if not logs:
            tk.Label(self.logs_frame, text="No logs").grid(row=0, column=0)
            return

        height_m = self.get_user_height_m()

        # Create header
        headers = ["Date", "Weight (lb)", "BMI", "Edit", "Delete"]
        for col, h in enumerate(headers):
            tk.Label(self.logs_frame, text=h, font=("Helvetica", 10, "bold")).grid(row=0, column=col, padx=5, pady=2)

        # Fill logs
        for row_idx, log in enumerate(logs, start=1):
            weight_lb = float(log['weight_kg']) / 0.453592
            bmi = float(log['weight_kg']) / (height_m ** 2)

            tk.Label(self.logs_frame, text=str(log['date'])).grid(row=row_idx, column=0, padx=5, pady=2)
            tk.Label(self.logs_frame, text=f"{weight_lb:.1f}").grid(row=row_idx, column=1, padx=5, pady=2)
            tk.Label(self.logs_frame, text=f"{bmi:.1f}").grid(row=row_idx, column=2, padx=5, pady=2)

            tk.Button(self.logs_frame, text="Edit", width=6, 
                    command=lambda l=log: self.edit_weight_log(l)).grid(row=row_idx, column=3, padx=5, pady=2)
            tk.Button(self.logs_frame, text="Delete", width=6, 
                    command=lambda l=log: self.delete_weight_log(l)).grid(row=row_idx, column=4, padx=5, pady=2)
