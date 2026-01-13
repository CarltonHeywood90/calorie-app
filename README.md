Calorie & Weight Tracker

A desktop application to track daily food intake, weight, and BMI, with personalized calorie goals and visualizations. Built with Python, Tkinter, Matplotlib, and MySQL, this app provides an intuitive dashboard to monitor nutrition and fitness progress.

Features
Food Tracking

Log meals by type: breakfast, lunch, dinner, and snack.

Track calories, macronutrients (protein, carbs, fat), and quantities.

Search and log food items from a database.

Edit or delete logged foods.

Daily summary of total calories consumed.

Weight & BMI Tracking

Log daily weight.

Automatic BMI calculation based on height and weight.

Historical weight and BMI trends displayed in an interactive chart.

Calorie Goals & Weight Loss Planning

Set daily calorie targets based on:

Age, height, weight, gender.

Activity level (sedentary to very active).

Set weight loss goals: 1 lb/week or 2 lbs/week.

Bar graph indicates whether daily intake is within target (green) or over target (red).

Dashboard

Combines food logs, weight logs, and charts in a single view.

Integrated calendar for selecting dates.

Responsive GUI layout optimized for high-resolution screens.

Real-time updates on data entry.

Architecture

Frontend: Tkinter GUI with modular frames

FoodEntryScreen – logs food intake, displays bar chart with calorie target.

WeightEntryScreen – logs weight and BMI, displays line chart.

CalorieGoalPanel – sets daily calorie target and weight loss goal.

Dashboard – orchestrates all panels and handles updates.

Backend: Python services interacting with MySQL

food_service.py – manages food logs, searches, and totals.

weight_service.py – manages weight logs, BMI calculations, and history.

Database: MySQL tables:

users – user info including age, height, weight, gender.

food_items – food catalog with calories and macronutrients.

food_logs – meals logged by user.

weight_logs – daily weight records.

Installation

Clone the repository:

git clone https://github.com/yourusername/calorie-tracker.git
cd calorie-tracker


Install Python dependencies:

pip install -r requirements.txt


Install and run MySQL, then create the database and tables:

CREATE DATABASE calorie_tracker;

USE calorie_tracker;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    height_cm FLOAT,
    weight_kg FLOAT,
    age INT,
    gender ENUM('male','female','other'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE food_items (
    food_id INT PRIMARY KEY,
    name VARCHAR(255),
    calories FLOAT,
    protein FLOAT,
    carbs FLOAT,
    fat FLOAT
);

CREATE TABLE food_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    food_id INT,
    meal_type ENUM('breakfast','lunch','dinner','snack'),
    quantity FLOAT,
    date DATE,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE weight_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    weight_kg FLOAT,
    log_date DATE,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);


Update backend/db/connection.py with your MySQL credentials.

Usage

Run the application:

python main.py


Log in or create a new account.

Enter personal information: height, weight, age, gender.

Set activity level and weight loss goal in Calorie Goal panel.

Log food intake and weight daily.

View charts and summaries in the dashboard.

Dependencies

Python 3.14+

Tkinter

MySQL Connector/Python (mysql-connector-python)

Matplotlib (matplotlib)

Project Structure
calorie-tracker/
├── backend/
│   ├── services/
│   │   ├── food_service.py
│   │   └── weight_service.py
│   └── db/
│       └── connection.py
├── gui/
│   ├── screens/
│   │   ├── dashboard.py
│   │   ├── food_entry.py
│   │   ├── weight_entry.py
│   │   └── login_screen.py
│   └── widgets/
│       └── calorie_goal.py
├── main.py
└── README.md

Future Enhancements

Multi-user support with secure password hashing.

Expanded food database with international foods.

Macronutrient visualizations (protein, carbs, fat) per meal.

Export data to CSV or PDF reports.

Notifications or reminders for food logging.

License

MIT License – see LICENSE file.
