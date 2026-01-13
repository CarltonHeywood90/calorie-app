import tkinter as tk
from gui.screens.food_entry import FoodEntryScreen
from gui.screens.weight_entry import WeightEntryScreen
from gui.widgets.calendar_panel import CalendarPanel
from gui.widgets.calorie_goal import CalorieGoalPanel
from datetime import date

class Dashboard(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent)
        self.parent = parent
        self.parent.geometry("1700x900")
        self.user = user
        self.user_id = user["user_id"]
        self.selected_date = date.today()

        # ---------- Main grid configuration ----------
        self.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1, uniform="col")
        self.columnconfigure(1, weight=1, uniform="col")
        self.rowconfigure(0, weight=0)  # top row (calendar + goal) minimal height
        self.rowconfigure(1, weight=1)  # bottom row (food + weight) expands

        # ---------- Header ----------
        tk.Label(self, text=f"Welcome, {user['username']}", font=("Helvetica", 16, "bold"))\
            .grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=10)

        # ---------- Top-left: Calendar ----------
        self.calendar = CalendarPanel(self, on_date_selected=self.on_date_selected)
        self.calendar.grid(row=1, column=0, sticky="nw", padx=20, pady=5)

        # ---------- Top-right: Calorie Goal ----------
        self.goal_panel = CalorieGoalPanel(self, user)
        self.goal_panel.grid(row=1, column=1, sticky="ne", padx=20, pady=5)

        # ---------- Bottom-left: Food Entry ----------
        self.food_panel = FoodEntryScreen(self, user_id=self.user_id)
        self.food_panel.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.rowconfigure(2, weight=1)  # allow food panel to expand
        self.columnconfigure(0, weight=1)  # allow left column to expand

        # ---------- Bottom-right: Weight Entry ----------
        self.weight_panel = WeightEntryScreen(self, user_id=self.user_id)
        self.weight_panel.grid(row=2, column=1, sticky="nsew", padx=20, pady=10)
        self.columnconfigure(1, weight=1)  # allow right column to expand

        # ---------- Initial load ----------
        self.update_daily_logs(self.selected_date)

    # ---------------- Calendar callback ----------------
    def on_date_selected(self, selected_date):
        self.selected_date = selected_date
        self.update_daily_logs(selected_date)

    # ---------------- Update all daily logs ----------------
    def update_daily_logs(self, log_date):
        # Update food and weight panels for the selected date
        self.food_panel.update_daily_logs(log_date)
        self.weight_panel.update_daily_logs(log_date)

        # Update food bar graph with calorie goal if applicable
        if hasattr(self, "goal_panel"):
            target = self.goal_panel.daily_target
            if target is not None:
                self.food_panel.update_bar_graph(target)
