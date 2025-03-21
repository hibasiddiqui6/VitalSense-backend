import os
import psycopg2
from psycopg2.extras import RealDictCursor
import firebase_admin
from firebase_admin import credentials, firestore

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

# --------------------- Firebase Firestore ---------------------------

# Load Firebase credential file path
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS")

# Initialize Firebase App
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)

# Get Firestore DB instance
db_firestore = firestore.client()

def insert_data(collection, data):
    try:
        doc_ref = db_firestore.collection(collection).document()
        doc_ref.set(data)
        print(f"✅ Data inserted into {collection}: {data}")
        return doc_ref.id
    except Exception as e:
        print(f"❌ Error inserting into Firestore: {e}")
        return None

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
        print(f"❌ Error fetching from Firestore: {e}")
        return None
