from backend.db.connection import create_connection

# -----------------------------
# Ensure a food exists in cache
# -----------------------------

def ensure_food(food_id, name, calories, protein, carbs, fat, serving_size=1):
    """
    Insert food into food_items if it does not already exist
    """
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT food_id FROM food_items WHERE food_id = %s", (food_id,))
    exists = cursor.fetchone()

    if not exists:
        cursor.execute("""
            INSERT INTO food_items (food_id, name, default_serving_size, calories, protein, carbs, fat)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (food_id, name, serving_size, calories, protein, carbs, fat))
        conn.commit()

    cursor.close()
    conn.close()

def log_food(user_id, food_id, name, calories, protein, carbs, fat, date, meal_type, quantity):
    """
    Adds a food entry for a user on a specific day & meal
    """
    ensure_food(food_id, name, calories, protein, carbs, fat)

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO food_logs (user_id, food_id, date, meal_type, quantity)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, food_id, date, meal_type, quantity))

    conn.commit()
    cursor.close()
    conn.close()

def get_day_log(user_id, date):
    """
    Returns all food entries for a user on a given date
    """
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT f.name, f.calories, f.protein, f.carbs, f.fat,
               l.quantity, l.meal_type
        FROM food_logs l
        JOIN food_items f ON l.food_id = f.food_id
        WHERE l.user_id = %s AND l.date = %s
    """, (user_id, date))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return rows

def get_day_totals(user_id, date):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            SUM(f.calories * l.quantity) AS calories,
            SUM(f.protein * l.quantity) AS protein,
            SUM(f.carbs * l.quantity) AS carbs,
            SUM(f.fat * l.quantity) AS fat
        FROM food_logs l
        JOIN food_items f ON l.food_id = f.food_id
        WHERE l.user_id = %s AND l.date = %s
    """, (user_id, date))

    totals = cursor.fetchone()
    cursor.close()
    conn.close()

    return totals
