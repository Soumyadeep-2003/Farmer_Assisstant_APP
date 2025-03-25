import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import os

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(os.environ["DATABASE_URL"])

def get_user_id(username):
    """Get user ID from username"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT id FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return user['id'] if user else None

def save_crop_details(user_id, crop_name, crop_type, planting_date, field_size, field_location=None):
    """Save new crop details to database"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO crop_details 
            (user_id, crop_name, crop_type, planting_date, field_size, field_location)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, crop_name, crop_type, planting_date, field_size, field_location))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving crop details: {e}")
        return False

def get_user_crops(user_id):
    """Get all crops for a user"""
    try:
        conn = get_db_connection()
        query = """
            SELECT * FROM crop_details 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        """
        return pd.read_sql(query, conn, params=(user_id,))
    except Exception as e:
        print(f"Error getting user crops: {e}")
        return pd.DataFrame()
    finally:
        conn.close()
