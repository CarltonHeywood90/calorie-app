import requests
import json
from backend.db.connection import create_connection
import os
from datetime import date

API_KEY = os.getenv("USDA_API_KEY")  # store in .env ideally
API_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

def search_food(query):
    """Search USDA API or cached JSON for food items"""
    try:
        with open("data/cached_foods.json", "r") as f:
            cached = json.load(f)
    except FileNotFoundError:
        cached = {}

    if query.lower() in cached:
        return cached[query.lower()]

    params = {
        "api_key": API_KEY,
        "query": query,
        "pageSize": 10
    }

    resp = requests.get(API_URL, params=params)
    resp.raise_for_status()
    results = resp.json().get("foods", [])

    foods = []
    for item in results:
        foods.append({
            "food_id": str(item["fdcId"]),
            "name": item.get("description", "Unknown"),
            "calories": next((n["value"] for n in item.get("foodNutrients", []) if n["nutrientName"]=="Energy"), 0),
            "protein": next((n["value"] for n in item.get("foodNutrients", []) if n["nutrientName"]=="Protein"), 0),
            "carbs": next((n["value"] for n in item.get("foodNutrients", []) if n["nutrientName"]=="Carbohydrate, by difference"), 0),
            "fat": next((n["value"] for n in item.get("foodNutrients", []) if n["nutrientName"]=="Total lipid (fat)"), 0)
        })

    cached[query.lower()] = foods
    with open("data/cached_foods.json", "w") as f:
        json.dump(cached, f, indent=2)

    return foods


def log_food(user_id, food_id, meal_type, quantity, log_date=None):
    log_date = log_date or date.today()
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO food_logs (user_id, food_id, date, meal_type, quantity)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE quantity = VALUES(quantity)
    """, (user_id, food_id, log_date, meal_type, quantity))

    conn.commit()
    cursor.close()
    conn.close()


def get_daily_food_logs(user_id, log_date=None):
    log_date = log_date or date.today()
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT fl.log_id, fl.food_id, fl.date, f.name, fl.meal_type, fl.quantity,
            f.calories * fl.quantity AS total_calories,
            f.protein * fl.quantity AS total_protein,
            f.carbs * fl.quantity AS total_carbs,
            f.fat * fl.quantity AS total_fat
        FROM food_logs fl
        JOIN food_items f ON fl.food_id = f.food_id
        WHERE fl.user_id = %s AND fl.date = %s
        ORDER BY fl.meal_type
    """, (user_id, log_date))


    logs = cursor.fetchall()
    cursor.close()
    conn.close()

    totals = {
        "calories": sum(l['total_calories'] for l in logs),
        "protein": sum(l['total_protein'] for l in logs),
        "carbs": sum(l['total_carbs'] for l in logs),
        "fat": sum(l['total_fat'] for l in logs)
    }

    return logs, totals

def update_food_log_quantity(user_id, food_id, log_date, meal_type, quantity):
    """
    Update the quantity of a food log entry for a specific user, meal, and date
    """
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE food_logs
        SET quantity = %s
        WHERE user_id = %s AND food_id = %s AND date = %s AND meal_type = %s
    """, (quantity, user_id, food_id, log_date, meal_type))
    conn.commit()
    cursor.close()
    conn.close()

def delete_food_log_entry(user_id, food_id, log_date, meal_type):
    """
    Delete a food log entry for a specific user, meal, and date
    """
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM food_logs
        WHERE user_id = %s AND food_id = %s AND date = %s AND meal_type = %s
    """, (user_id, food_id, log_date, meal_type))
    conn.commit()
    cursor.close()
    conn.close()
