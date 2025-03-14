import mysql.connector
from mysql.connector import Error

# Database connection setup
def get_db_connection():
    try:
        # Try connecting to the database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Hiba@123",
            database="vitalsense_db"
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: Unable to connect to the database. {e}")
        raise e  # Reraise the error after logging it

# Function to execute SELECT queries
def fetch_data(query, params=None):
    db = None
    cursor = None
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute(query, params or ())
        result = cursor.fetchone()  # Fetch a single result, not all results
        return result  # Return the first (or None if not found)
    except Error as e:
        print(f"Error executing SELECT query: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

def fetch_all_data(query, params=None):
    db = None
    cursor = None
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute(query, params or ())
        results = cursor.fetchall()  # Fetch all matching records
        return results  # Return a list of results
    except Error as e:
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
    except Error as e:
        print(f"Error executing query: {e}")
        db.rollback()  # Rollback in case of an error
        raise e  # Reraise the error after logging it
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin
cred = credentials.Certificate("/etc/secrets/firebase_credentials.json")
firebase_admin.initialize_app(cred)

# Get Firestore DB instance
db = firestore.client()

# Function to insert data into Firestore
def insert_data(collection, data):
    try:
        doc_ref = db.collection(collection).document()
        doc_ref.set(data)
        print(f"✅ Data inserted into {collection}: {data}")
        return doc_ref.id
    except Exception as e:
        print(f"❌ Error inserting data: {e}")
        return None

# Function to fetch the latest document from Firestore
def fetch_latest_data(collection, field, value):
    try:
        # Ensure Firestore query includes sorting (required for indexes)
        docs = db.collection(collection).where(field, "==", value).order_by("timestamp", direction=firestore.Query.DESCENDING).limit(1).stream()

        for doc in docs:
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None

