from backend.db.connection import create_connection

def get_user_id(user):
    if isinstance(user, dict):
        return int(user["user_id"])
    return int(user)

def log_weight(user_id: int, log_date, weight_kg: float):
    """
    Insert a new weight log.
    """
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO weight_logs (user_id, date, weight_kg)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE weight_kg = VALUES(weight_kg)
        """, (user_id, log_date, weight_kg))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_weight_logs_for_user(user_id: int):
    """
    Get all weight logs for a user, ordered by date.
    """
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT log_id, date, weight_kg
            FROM weight_logs
            WHERE user_id = %s
            ORDER BY date
        """, (user_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def update_weight_log(log_id: int, weight_kg: float):
    """
    Update an existing weight log's weight.
    """
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE weight_logs
            SET weight_kg = %s
            WHERE log_id = %s
        """, (weight_kg, log_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def delete_weight_log(log_id: int):
    """
    Delete a weight log by its log_id.
    """
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            DELETE FROM weight_logs
            WHERE log_id = %s
        """, (log_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def get_weight_history(user):
    user_id = get_user_id(user)

    conn = create_connection()
    if not conn:
        return []

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT log_id, weight_kg, date FROM weight_logs WHERE user_id = %s ORDER BY date ASC",
            (user_id,)
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_weight_history_with_bmi(user_id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)  # dictionary cursor

    # Get weight logs
    cursor.execute(
        "SELECT weight_kg, date FROM weight_logs WHERE user_id = %s ORDER BY date ASC",
        (user_id,)
    )
    logs = cursor.fetchall()  # each row is a dict

    # Get user height
    cursor.execute("SELECT height_cm FROM users WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()  # dict because dictionary=True
    height_m = row['height_cm'] if row and row['height_cm'] else 1.75  # fallback if not set

    # Compute BMI for each log
    for log in logs:
        log['bmi'] = float(log['weight_kg']) / (height_m ** 2)

    cursor.close()
    conn.close()
    return logs
