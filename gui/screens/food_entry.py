import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from backend.services.food_service import get_daily_food_logs, search_food, log_food, update_food_log_quantity
from backend.db.connection import create_connection
from datetime import date
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class FoodEntryScreen(tk.Frame):
    MEALS = ['breakfast', 'lunch', 'dinner', 'snack']

    def __init__(self, parent, user_id):
        super().__init__(parent)
        self.user_id = user_id
        self.current_results = []
        self.current_date = date.today()
        self.daily_budget = 2000  # default daily calories
        self.planned_deficit = 0  # default deficit

        # ---------- Layout ----------
        self.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(1, weight=1)
        self.rowconfigure(6, weight=1)  # logs & chart expand

        # Header
        tk.Label(self, text="Food Entry", font=("Helvetica", 16, "bold"))\
            .grid(row=0, column=0, columnspan=3, pady=10)

        # Meal selector
        tk.Label(self, text="Meal Type:").grid(row=1, column=0, sticky="w", padx=5)
        self.meal_var = tk.StringVar(value=self.MEALS[0])
        ttk.OptionMenu(self, self.meal_var, self.MEALS[0], *self.MEALS).grid(row=1, column=1, sticky="w")

        # Food search
        tk.Label(self, text="Food Name:").grid(row=2, column=0, sticky="w", padx=5)
        self.food_entry = tk.Entry(self, width=30)
        self.food_entry.grid(row=2, column=1, sticky="w")
        tk.Button(self, text="Search", command=self.search_food).grid(row=2, column=2, padx=5)

        # Search results
        self.results_listbox = tk.Listbox(self, width=50, height=6)
        self.results_listbox.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        # Quantity + log
        tk.Label(self, text="Quantity (servings):").grid(row=4, column=0, sticky="w", padx=5)
        self.qty_entry = tk.Entry(self, width=5)
        self.qty_entry.grid(row=4, column=1, sticky="w")
        self.qty_entry.insert(0, "1")
        tk.Button(self, text="Log Food", command=self.log_selected_food).grid(row=4, column=2, padx=5)

        # Total calories & budget
        self.total_calories_label = tk.Label(self, text="Total Calories: 0")
        self.total_calories_label.grid(row=5, column=0, columnspan=2, sticky="w", pady=5)
        tk.Button(self, text="Set Daily Budget / Deficit", command=self.set_daily_budget)\
            .grid(row=5, column=2, padx=5)

        # Logs frame
        self.logs_frame = tk.Frame(self, bd=1, relief="sunken")
        self.logs_frame.grid(row=6, column=0, columnspan=3, sticky="nsew", pady=5)
        self.logs_frame.columnconfigure(0, weight=1)

        # Chart frame
        self.chart_frame = tk.Frame(self)
        self.chart_frame.grid(row=7, column=0, columnspan=3, sticky="nsew", pady=10)
        self.chart_frame.columnconfigure(0, weight=1)
        self.chart_frame.rowconfigure(0, weight=1)
        self.canvas = None

        # Initial load
        self.update_daily_logs(self.current_date)

    # ----------------- Update logs -----------------
    def update_daily_logs(self, log_date):
        self.current_date = log_date

        # Clear logs
        for widget in self.logs_frame.winfo_children():
            widget.destroy()

        logs, totals = get_daily_food_logs(self.user_id, log_date=log_date)

        total_calories = sum(log['total_calories'] for log in logs) if logs else 0
        target = self.daily_budget - self.planned_deficit
        self.total_calories_label.config(
            text=f"Total Calories: {total_calories} / Target: {target}"
        )

        if not logs:
            tk.Label(self.logs_frame, text="No foods logged for this day").grid(sticky="w")
            self.create_calorie_chart(total_calories)
            return

        # Group by meal
        meals = {meal: [] for meal in self.MEALS}
        for log in logs:
            meals[log['meal_type']].append(log)

        row_idx = 0
        for meal, items in meals.items():
            if not items:
                continue
            tk.Label(self.logs_frame, text=meal.capitalize(), font=("Helvetica", 12, "bold"))\
                .grid(row=row_idx, column=0, sticky="w", pady=(5,0))
            row_idx += 1
            for log in items:
                tk.Label(self.logs_frame, text=f"{log['name']} x {log['quantity']} | {log['total_calories']} kcal")\
                    .grid(row=row_idx, column=0, sticky="w")
                tk.Button(self.logs_frame, text="Edit", width=5, command=lambda l=log: self.edit_food_log(l))\
                    .grid(row=row_idx, column=1, padx=5)
                tk.Button(self.logs_frame, text="Delete", width=5, command=lambda l=log: self.delete_food_log(l))\
                    .grid(row=row_idx, column=2, padx=5)
                row_idx += 1

        # Update chart
        self.create_calorie_chart(total_calories)

    # ----------------- CRUD -----------------
    def search_food(self):
        query = self.food_entry.get()
        if not query:
            messagebox.showwarning("Input required", "Enter a food name to search.")
            return
        results = search_food(query)
        self.current_results = results
        self.results_listbox.delete(0, tk.END)
        for food in results:
            self.results_listbox.insert(
                tk.END, f"{food['name']} (Calories: {food.get('calories','N/A')})"
            )

    def log_selected_food(self):
        selection = self.results_listbox.curselection()
        if not selection:
            messagebox.showwarning("Select a food", "Please select a food from the list.")
            return
        food = self.current_results[selection[0]]

        try:
            qty = float(self.qty_entry.get())
        except ValueError:
            messagebox.showerror("Invalid quantity", "Enter a valid number.")
            return

        self.add_food_item_if_not_exists(food)
        log_food(self.user_id, food['food_id'], self.meal_var.get(), qty, self.current_date)
        self.update_daily_logs(self.current_date)

    def edit_food_log(self, log):
        from tkinter.simpledialog import askfloat
        new_qty = askfloat("Edit Quantity", f"{log['name']} ({log['meal_type']}):", initialvalue=log['quantity'])
        if new_qty is None:
            return
        update_food_log_quantity(self.user_id, log['food_id'], log['meal_type'], new_qty, log['date'])
        self.update_daily_logs(self.current_date)

    def delete_food_log(self, log):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM food_logs WHERE log_id=%s", (log['log_id'],))
        conn.commit()
        cursor.close()
        conn.close()
        self.update_daily_logs(self.current_date)

    def add_food_item_if_not_exists(self, food):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT IGNORE INTO food_items (food_id, name, calories, protein, carbs, fat)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            food['food_id'],
            food['name'],
            food.get('calories', 0),
            food.get('protein', 0),
            food.get('carbs', 0),
            food.get('fat', 0)
        ))
        conn.commit()
        cursor.close()
        conn.close()

    # ----------------- Budget / Deficit -----------------
    def set_daily_budget(self):
        budget = simpledialog.askinteger("Daily Calorie Budget", "Enter your daily calorie budget:")
        if budget:
            self.daily_budget = budget
        deficit = simpledialog.askinteger("Planned Deficit", "Enter planned calorie deficit:")
        if deficit is not None:
            self.planned_deficit = deficit
        self.update_daily_logs(self.current_date)

    # ----------------- Calorie Chart -----------------
    def create_calorie_chart(self, total_calories):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        target = self.daily_budget - self.planned_deficit
        color = 'green' if total_calories <= target else 'red'

        fig = Figure(figsize=(6,3), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(['Calories'], [total_calories], color=color)
        ax.axhline(target, color='blue', linestyle='--', label='Planned Target')
        ax.set_ylabel("Calories")
        ax.set_ylim(0, max(total_calories, target) * 1.2)
        ax.legend()
        ax.grid(True)

        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def update_bar_graph(self, daily_target):
        # Placeholder: just store the target
        self.daily_target = daily_target
        # You can later implement the actual matplotlib bar chart
        print(f"Food bar graph updated with target: {daily_target}")

