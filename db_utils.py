import os
import psycopg2
from psycopg2.extras import RealDictCursor

# --------------------- PostgreSQL Connection ---------------------------

# Load database connection string from environment
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    try:
        connection = psycopg2.connect(DATABASE_URL)
        return connection
    except Exception as e:
        print(f"❌ Error: Unable to connect to the database. {e}")
        raise e

# Execute SELECT query (single row)
def fetch_data(query, params=None):
    db = None
    cursor = None
    try:
        db = get_db_connection()
        cursor = db.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params or ())
        return cursor.fetchone()
    except Exception as e:
        print(f"❌ Error executing SELECT query: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

# Execute SELECT query (all rows)
def fetch_all_data(query, params=None):
    db = None
    cursor = None
    try:
        db = get_db_connection()
        cursor = db.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params or ())
        return cursor.fetchall()
    except Exception as e:
        print(f"❌ Error executing SELECT ALL query: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

# Execute INSERT, UPDATE, DELETE
def modify_data(query, params=None):
    db = None
    cursor = None
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(query, params or ())
        db.commit()
    except Exception as e:
        print(f"❌ Error executing query: {e}")
        db.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

def fetch_latest_data(table, column, value):
    sql = f"""
        SELECT * FROM {table}
        WHERE {column} = %s
        ORDER BY timestamp DESC, id DESC
        LIMIT 1
    """
    return fetch_data(sql, (value,))