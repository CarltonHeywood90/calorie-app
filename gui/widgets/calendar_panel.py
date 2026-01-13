# gui/widgets/calendar_panel.py
import tkinter as tk
from tkcalendar import Calendar
from datetime import date

class CalendarPanel(tk.Frame):
    def __init__(self, parent, on_date_selected=None):
        super().__init__(parent)
        self.parent = parent
        self.on_date_selected = on_date_selected
        self.selected_date = date.today()

        self.calendar = Calendar(
            self,
            selectmode="day",
            year=self.selected_date.year,
            month=self.selected_date.month,
            day=self.selected_date.day,
            date_pattern="yyyy-mm-dd"
        )
        self.calendar.pack(padx=10, pady=5)
        self.calendar.bind("<<CalendarSelected>>", self.date_selected)

    def date_selected(self, event=None):
        self.selected_date = self.calendar.get_date()
        # convert string to date object if necessary
        if isinstance(self.selected_date, str):
            y, m, d = map(int, self.selected_date.split('-'))
            self.selected_date = date(y, m, d)
        if self.on_date_selected:
            self.on_date_selected(self.selected_date)
