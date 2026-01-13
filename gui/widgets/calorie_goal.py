import tkinter as tk
from tkinter import ttk
from backend.db.connection import create_connection

# Activity multipliers based on Harris-Benedict Equation
ACTIVITY_LEVELS = {
    "Sedentary (little/no exercise)": 1.2,
    "Lightly Active (light exercise 1-3 days/week)": 1.375,
    "Moderately Active (moderate exercise 3-5 days/week)": 1.55,
    "Very Active (hard exercise 6-7 days/week)": 1.725,
    "Extra Active (very hard exercise & physical job)": 1.9
}

# Weight loss goals in lbs/week
WEIGHT_LOSS_GOALS = {
    "Maintain Weight": 0,
    "1 lb/week": 1,
    "2 lbs/week": 2
}

class CalorieGoalPanel(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bd=1, relief="groove", padx=10, pady=10)
        self.user = user
        self.user_id = user["user_id"]

        # Variables
        self.activity_var = tk.StringVar(value=list(ACTIVITY_LEVELS.keys())[0])
        self.goal_var = tk.StringVar(value=list(WEIGHT_LOSS_GOALS.keys())[0])
        self.daily_target = 0  # calories

        # ---------- Title ----------
        tk.Label(self, text="Daily Calorie Goal", font=("Helvetica", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(0,10))

        # ---------- Activity Level ----------
        tk.Label(self, text="Activity Level:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.OptionMenu(self, self.activity_var, self.activity_var.get(), *ACTIVITY_LEVELS.keys(), command=self.calculate_target)\
            .grid(row=1, column=1, sticky="ew", pady=2)

        # ---------- Weight Goal ----------
        tk.Label(self, text="Weight Goal:").grid(row=2, column=0, sticky="w", pady=2)
        ttk.OptionMenu(self, self.goal_var, self.goal_var.get(), *WEIGHT_LOSS_GOALS.keys(), command=self.calculate_target)\
            .grid(row=2, column=1, sticky="ew", pady=2)

        # ---------- Display Target ----------
        self.target_label = tk.Label(self, text="Target: -- kcal", font=("Helvetica", 10, "bold"))
        self.target_label.grid(row=3, column=0, columnspan=2, pady=(10,0))

        # Initial calculation
        self.calculate_target()

    # ------------------- Calculate daily target -------------------
    def calculate_target(self, *_):
        """Compute BMR and adjust for activity + weight loss goal"""
        # Get user height, weight, age, gender
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT weight_kg, height_cm, age, gender FROM users WHERE user_id=%s", (self.user_id,))
        user_row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user_row:
            self.daily_target = 2000  # fallback
            self.target_label.config(text=f"Target: {self.daily_target} kcal")
            return

        weight_kg = float(user_row['weight_kg'])
        height_cm = float(user_row['height_cm'])
        age = int(user_row['age'])
        gender = user_row['gender']

        # Harris-Benedict BMR
        if gender.lower() == "male":
            bmr = 88.36 + (13.4 * weight_kg) + (4.8 * height_cm) - (5.7 * age)
        else:
            bmr = 447.6 + (9.2 * weight_kg) + (3.1 * height_cm) - (4.3 * age)

        # Activity multiplier
        activity_multiplier = ACTIVITY_LEVELS.get(self.activity_var.get(), 1.2)
        maintenance_calories = bmr * activity_multiplier

        # Adjust for weight loss goal
        lbs_per_week = WEIGHT_LOSS_GOALS.get(self.goal_var.get(), 0)
        # 1 lb fat ≈ 3500 kcal
        daily_deficit = (lbs_per_week * 3500) / 7
        self.daily_target = max(0, int(maintenance_calories - daily_deficit))

        # Update label
        self.target_label.config(text=f"Target: {self.daily_target} kcal")

    # ------------------- Getter -------------------
    def get_daily_target(self):
        return self.daily_target
