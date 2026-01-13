# backend/auth/auth.py

import bcrypt
from backend.db.connection import create_connection

def register_user(username, password, height_cm=None, weight_kg=None, gender=None):
    """Register a new user with hashed password"""
    conn = create_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    # Hash the password
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, height_cm, weight_kg, gender) "
            "VALUES (%s, %s, %s, %s, %s)",
            (username, hashed, height_cm, weight_kg, gender)
        )
        conn.commit()
        print(f"User '{username}' registered successfully.")
        return True
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def login_user(username, password):
    """Verify user credentials"""
    conn = create_connection()
    if not conn:
        return False
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM users WHERE username = %s",
            (username,)
        )
        user = cursor.fetchone()
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            print(f"User '{username}' logged in successfully.")
            return user  # return full user info
        else:
            print("Invalid username or password.")
            return None
    finally:
        cursor.close()
        conn.close()

def get_user_by_id(user_id):
    """Fetch user info by user_id"""
    conn = create_connection()
    if not conn:
        return None

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def update_user(user_id, height_cm=None, weight_kg=None, password=None):
    """Update user info"""
    conn = create_connection()
    if not conn:
        return False

    cursor = conn.cursor()
    try:
        if password:
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("UPDATE users SET password_hash=%s WHERE user_id=%s", (hashed, user_id))
        if height_cm is not None:
            cursor.execute("UPDATE users SET height_cm=%s WHERE user_id=%s", (height_cm, user_id))
        if weight_kg is not None:
            cursor.execute("UPDATE users SET weight_kg=%s WHERE user_id=%s", (weight_kg, user_id))
        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()
