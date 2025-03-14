import psycopg2
from psycopg2.extras import RealDictCursor
import firebase_admin
from firebase_admin import credentials, firestore

# --------------------- PostgreSQL Connection ---------------------------

# Database connection setup
def get_db_connection():
    try:
        connection = psycopg2.connect(
            host="dpg-cvaavhin91rc7392d75g-a.oregon-postgres.render.com",  # Render PostgreSQL host
            database="vitalsense_db",  # Database name
            user="vitalsenseroot",
            password="qnWmiYp7bIA7cw1MNN3O48yocAn4M0ZS",
            port=5432
        )
        return connection
    except Exception as e:
        print(f"Error: Unable to connect to the database. {e}")
        raise e


# Function to execute SELECT queries (single row)
def fetch_data(query, params=None):
    db = None
    cursor = None
    try:
        db = get_db_connection()
        cursor = db.cursor(cursor_factory=RealDictCursor)  # ✅ Correct for PostgreSQL
        cursor.execute(query, params or ())
        result = cursor.fetchone()  # Fetch a single result
        return result
    except Exception as e:
        print(f"Error executing SELECT query: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# Function to execute SELECT queries (all rows)
def fetch_all_data(query, params=None):
    db = None
    cursor = None
    try:
        db = get_db_connection()
        cursor = db.cursor(cursor_factory=RealDictCursor)  # ✅ Correct for PostgreSQL
        cursor.execute(query, params or ())
        results = cursor.fetchall()  # Fetch all records
        return results
    except Exception as e:
        print(f"Error executing SELECT query: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# Function to execute INSERT, UPDATE, DELETE queries
def modify_data(query, params=None):
    db = None
    cursor = None
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(query, params or ())
        db.commit()
    except Exception as e:
        print(f"Error executing query: {e}")
        db.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

# --------------------- Firebase Firestore ---------------------------

# Initialize Firebase Admin
cred = credentials.Certificate("/etc/secrets/firebase_credentials.json")
firebase_admin.initialize_app(cred)

# Get Firestore DB instance
db_firestore = firestore.client()


# Function to insert data into Firestore
def insert_data(collection, data):
    try:
        doc_ref = db_firestore.collection(collection).document()
        doc_ref.set(data)
        print(f"✅ Data inserted into {collection}: {data}")
        return doc_ref.id
    except Exception as e:
        print(f"❌ Error inserting data: {e}")
        return None


# Function to fetch the latest document from Firestore
def fetch_latest_data(collection, field, value):
    try:
        docs = (
            db_firestore.collection(collection)
            .where(field, "==", value)
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(1)
            .stream()
        )
        for doc in docs:
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None
