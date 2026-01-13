import tkinter as tk
from tkcalendar import Calendar
from gui.screens.food_entry import FoodEntryScreen
from datetime import date, datetime
from tkinter import messagebox

class CalendarFoodApp(tk.Frame):
    def __init__(self, parent, user_id):  # <- accept user_id
        super().__init__(parent)
        self.user_id = user_id
        self.pack(fill="both", expand=True)

        # Selected date
        self.selected_date = None

        # Calendar
        cal_frame = tk.Frame(self)
        cal_frame.pack(pady=10)

        self.cal = Calendar(cal_frame, selectmode='day', year=2026, month=1, day=1)
        self.cal.pack()

        tk.Button(cal_frame, text="Load Day", command=self.load_selected_day).pack(pady=5)

        # Food entry screen
        self.food_screen = FoodEntryScreen(self, user_id=user_id)
        self.food_screen.pack(fill="both", expand=True)

    def load_selected_day(self, event=None):
        # Get selected date from tkcalendar
        raw_date = self.cal.get_date()  # e.g., '1/21/26'
        selected_date = datetime.strptime(raw_date, "%m/%d/%y").date()

        if selected_date > date.today():
            messagebox.showwarning(
                "Future date",
                "The selected date is in the future. Nothing to show or log."
            )
            return

        self.selected_date = selected_date
        self.food_screen.update_daily_logs(log_date=self.selected_date)

