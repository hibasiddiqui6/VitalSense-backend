from flask import Flask, request, jsonify
from flask_cors import CORS
import bcrypt  # For secure password hashing
from db_utils import fetch_data, fetch_all_data, modify_data, get_db_connection, insert_data, fetch_latest_data  # Import database utility functions
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Store received sensor data (temporary storage for testing)
sensor_data = {}

#Register a Patient
@app.route('/register/patient', methods=['POST'])
def register_patient():
    data = request.json
    try:
        # Hash the password using bcrypt
        hashed_password = bcrypt.hashpw(data['Password'].encode(), bcrypt.gensalt())

        # Insert the new user into the users table
        sql_user = """
        INSERT INTO users (FullName, Email, Password, Role) 
        VALUES (%s, %s, %s, %s)
        """
        modify_data(sql_user, (data['FullName'], data['Email'], hashed_password, 'patient'))

        # Retrieve UserID by looking up the user via email
        sql_check_user = "SELECT UserID FROM users WHERE Email = %s"
        user_check_result = fetch_data(sql_check_user, (data['Email'],))

        if user_check_result is None:
            return jsonify({"error": "Failed to retrieve UserID from users table"}), 500

        user_id = user_check_result['UserID']
        print(f"Retrieved UserID from users table: {user_id}")  # Debugging output

        # Now insert the patient details into the patients table
        sql_patient = """
        INSERT INTO patients (UserID, Gender, Age, Contact) 
        VALUES (%s, %s, %s, %s)
        """
        modify_data(sql_patient, (user_id, data['Gender'], data['Age'], data['Contact']))

        return jsonify({"message": "Patient registered successfully!"}), 201
    except Exception as e:
        print(f"Error: {e}")  # Debugging the full error
        return jsonify({"error": f"An error occurred: {e}"}), 500

# Login for a patient
@app.route('/login/patient', methods=['POST'])
def login_patient():
    data = request.json
    try:
        # Fetch the user data based on the email
        sql = "SELECT * FROM users WHERE Email = %s"
        user = fetch_data(sql, (data['Email'],))

        if user and user['Role'] == 'patient':  # Ensure user exists and is a patient
            # Fetch the patient details based on UserID
            sql_patient = "SELECT * FROM patients WHERE UserID = %s"
            patient = fetch_data(sql_patient, (user['UserID'],))

            if patient:  # Ensure patient details exist
                # Check the hashed password using bcrypt
                if bcrypt.checkpw(data['Password'].encode(), user['Password'].encode('utf-8')):
                    return jsonify({"message": "Login successful!", "patient_id": patient['PatientID']}), 200
                else:
                    return jsonify({"message": "Invalid email or password"}), 401
            else:
                return jsonify({"message": "Patient details not found"}), 404
        else:
            return jsonify({"message": "Invalid email or password"}), 401
    except Exception as e:
        return jsonify({"error": "An error occurred, please try again later."}), 500

# Register a Specialist
@app.route('/register/specialist', methods=['POST'])
def register_specialist():
    data = request.json
    try:
        # Hash the password using bcrypt
        hashed_password = bcrypt.hashpw(data['Password'].encode(), bcrypt.gensalt())

        # Insert the new user into the users table
        sql_user = """
        INSERT INTO users (FullName, Email, Password, Role) 
        VALUES (%s, %s, %s, %s)
        """
        modify_data(sql_user, (data['FullName'], data['Email'], hashed_password, 'specialist'))

        # Retrieve UserID by looking up the user via email
        sql_check_user = "SELECT UserID FROM users WHERE Email = %s"
        user_check_result = fetch_data(sql_check_user, (data['Email'],))

        if user_check_result is None:
            return jsonify({"error": "Failed to retrieve UserID from users table"}), 500

        user_id = user_check_result['UserID']
        print(f"Retrieved UserID from users table: {user_id}")  # Debugging output

        # Now insert the specialist details into the health_specialist table
        sql_specialist = """
        INSERT INTO health_specialist (UserID, Profession, Speciality) 
        VALUES (%s, %s, %s)
        """
        modify_data(sql_specialist, (user_id, data['Profession'], data['Speciality']))

        return jsonify({"message": "Specialist registered successfully!"}), 201
    except Exception as e:
        print(f"Error: {e}")  # Debugging the full error
        return jsonify({"error": f"An error occurred: {e}"}), 500

# Login for a health specialist
@app.route('/login/specialist', methods=['POST'])
def login_specialist():
    data = request.json
    try:
        # Fetch the user data based on the email
        sql = "SELECT * FROM users WHERE Email = %s"
        user = fetch_data(sql, (data['Email'],))

        if user and user['Role'] == 'specialist':  # ✅ Correct role check
            # Fetch the health specialist details based on UserID
            sql_specialist = "SELECT * FROM health_specialist WHERE UserID = %s"
            specialist = fetch_data(sql_specialist, (user['UserID'],))

            if specialist:  # Ensure health specialist details exist
                # Check the hashed password using bcrypt
                if bcrypt.checkpw(data['Password'].encode(), user['Password'].encode('utf-8')):
                    return jsonify({"message": "Login successful!", "specialist_id": specialist['SpecialistID']}), 200
                else:
                    return jsonify({"message": "Invalid email or password"}), 401
            else:
                return jsonify({"message": "Health specialist details not found"}), 404
        else:
            return jsonify({"message": "Invalid email or password"}), 401
    except Exception as e:
        return jsonify({"error": "An error occurred, please try again later."}), 500

#Only MySQL
# @app.route('/sensor', methods=['POST'])
# def receive_sensor_data():
#     global sensor_data
#     try:
#         data = request.json
#         ecg = data.get("ecg", None)
#         respiration = data.get("respiration", None)
#         temperature = data.get("temperature", None)

#         # **Find Patient ID and SmartShirt ID for this session**
#         sql_query = """
#         SELECT smartshirt.patientID, smartshirt.smartshirtID 
#         FROM smartshirt 
#         JOIN patients ON smartshirt.patientID = patients.PatientID 
#         LIMIT 1
#         """
#         result = fetch_data(sql_query)

#         if not result:
#             return jsonify({"error": "No SmartShirt is linked to a patient."}), 404

#         patient_id = result["patientID"]
#         smartshirt_id = result["smartshirtID"]

#         # **Format timestamp with milliseconds**
#         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  

#         # **Store latest data in memory for real-time access**
#         sensor_data = {
#             "ecg": ecg,
#             "respiration": respiration,
#             "temperature": temperature,
#             "timestamp": timestamp
#         }

#         print(f"✅ Received Data for Patient {patient_id}: {sensor_data}")

#         # **Save Data into `health_vitals` Table**
#         sql_insert = """
#         INSERT INTO health_vitals (timestamp, ecg, respiration_rate, temperature, patientID, smartshirtID) 
#         VALUES (%s, %s, %s, %s, %s, %s)
#         """
#         modify_data(sql_insert, (timestamp, ecg, respiration, temperature, patient_id, smartshirt_id))

#         return jsonify({"status": "success", "data": sensor_data}), 200

#     except Exception as e:
#         return jsonify({"error": f"An error occurred: {e}"}), 500

# @app.route('/get_sensor', methods=['GET'])
# def get_sensor_data():
#     try:
#         patient_id = request.args.get("patient_id")
#         print(f"🟢 Received patient_id: {patient_id}")  # Debugging output

#         if not patient_id:
#             return jsonify({"error": "Patient ID is required"}), 400

#         # **Fetch latest sensor data from `health_vitals` for the given patient**
#         sql_query = """
#         SELECT timestamp, ecg, respiration_rate, temperature 
#         FROM health_vitals 
#         WHERE patientID = %s 
#         ORDER BY timestamp DESC 
#         LIMIT 1
#         """
#         latest_data = fetch_data(sql_query, (patient_id,))

#         if not latest_data:
#             return jsonify({"error": "No sensor data found for this patient"}), 404
        
#         # **Check if the record is older than 10 seconds**
#         current_time = datetime.now()
#         record_time = latest_data['timestamp']

#         if (current_time - record_time).total_seconds() > 10:
#             return jsonify({"error": "Sensor data is outdated"}), 408  # HTTP 408: Request Timeout

#         return jsonify(latest_data), 200

#     except Exception as e:
#         return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/get_patient_id', methods=['GET'])
def get_patient_id():
    """Fetches the patient ID and role using the email address."""
    try:
        email = request.args.get("email")
        if not email:
            return jsonify({"error": "Email is required"}), 400

        # Fetch user details using email
        sql_user = "SELECT UserID, Role FROM users WHERE Email = %s"
        user = fetch_data(sql_user, (email,))

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Fetch the corresponding patient ID
        sql_patient = "SELECT PatientID FROM patients WHERE UserID = %s"
        patient = fetch_data(sql_patient, (user['UserID'],))

        if not patient:
            return jsonify({"error": "Patient record not found"}), 404

        # Return both patient_id and role
        return jsonify({"patient_id": patient['PatientID'], "role": user['Role']}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/get_specialist_id', methods=['GET'])
def get_specialist_id():
    """Fetches the specialist ID using the email address."""
    try:
        email = request.args.get("email")
        if not email:
            return jsonify({"error": "Email is required"}), 400

        # Fetch user details using email
        sql_user = "SELECT UserID, Role FROM users WHERE Email = %s"
        user = fetch_data(sql_user, (email,))

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Fetch the corresponding specialist ID
        sql_specialist = "SELECT SpecialistID FROM health_specialist WHERE UserID = %s"
        specialist = fetch_data(sql_specialist, (user['UserID'],))

        if not specialist:
            return jsonify({"error": "Specialist record not found"}), 404

        return jsonify({"specialist_id": specialist['SpecialistID'], "role": user['Role']}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
    
@app.route('/register_mac', methods=['POST'])
def register_mac():
    """Registers the ESP32 MAC address separately before sending sensor data."""
    try:
        data = request.json
        mac_address = data.get("mac_address")
        patient_id = data.get("patient_id")

        if not mac_address or not patient_id:
            return jsonify({"error": "MAC address and patient ID are required"}), 400

        # Check if the patient exists
        patient_check = fetch_data("SELECT * FROM patients WHERE PatientID = %s", (patient_id,))
        if not patient_check:
            return jsonify({"error": "Invalid Patient ID. Patient does not exist."}), 404

        # Check if the SmartShirt is already registered
        existing_entry = fetch_data("SELECT * FROM smartshirt WHERE DeviceMAC = %s", (mac_address,))
        if existing_entry:
            return jsonify({"message": "SmartShirt already registered!", "smartshirt_id": existing_entry['smartshirtID']}), 200

        # Register new SmartShirt
        sql = "INSERT INTO smartshirt (patientID, DeviceMAC, ShirtStatus) VALUES (%s, %s, %s)"
        modify_data(sql, (patient_id, mac_address, True))

        return jsonify({"message": "MAC registered successfully!"}), 201

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/check_smartshirt', methods=['GET'])
def check_smartshirt():
    try:
        mac_address = request.args.get("mac_address")
        if not mac_address:
            return jsonify({"error": "MAC address is required"}), 400

        result = fetch_data("SELECT DeviceMAC, ShirtStatus FROM smartshirt WHERE DeviceMAC = %s", (mac_address,))
        if result:
            return jsonify({"exists": True, "shirt_status": bool(result["ShirtStatus"])}), 200
        else:
            return jsonify({"exists": False}), 404
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/get_smartshirts', methods=['GET'])
def get_smartshirts():
    try:
        patient_id = request.args.get("patient_id")
        if not patient_id:
            return jsonify({"error": "Patient ID is required"}), 400

        results = fetch_all_data("SELECT DeviceMAC, ShirtStatus FROM smartshirt WHERE patientID = %s", (patient_id,))
        if results:
            # Convert ShirtStatus to boolean
            for result in results:
                result["ShirtStatus"] = bool(result["ShirtStatus"])
            return jsonify({"smartshirts": results}), 200
        else:
            return jsonify({"message": "No SmartShirts found"}), 404
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
    
@app.route('/send_mac_to_app', methods=['POST'])
def receive_mac_from_esp():
    try:
        data = request.json
        mac_address = data.get("mac_address")

        if not mac_address:
            return jsonify({"error": "MAC address is required"}), 400

        print(f"Received MAC Address from ESP32: {mac_address}")

        return jsonify({"message": "MAC Address received successfully!"}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/get_patient_profile', methods=['GET'])
def get_patient_profile():
    try:
        patient_id = request.args.get("patient_id")

        if not patient_id:
            return jsonify({"error": "Patient ID is required"}), 400

        print(f"🟢 Fetching profile for Patient ID: {patient_id}")

        # **SQL Query to fetch FullName, Gender, and Age**
        sql_query = """
        SELECT u.FullName, u.Email, p.Gender, p.Age, p.Contact, p.PatientID
        FROM patients p
        JOIN users u ON p.UserID = u.UserID
        WHERE p.patientID = %s
        """
        #, p.Weight
        patient_profile = fetch_data(sql_query, (patient_id,))

        if not patient_profile:
            return jsonify({"error": "No user profile found"}), 404

        return jsonify(patient_profile), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/get_specialist_profile', methods=['GET'])
def get_specialist_profile():
    try:
        specialist_id = request.args.get("specialist_id")

        if not specialist_id:
            return jsonify({"error": "Specialist ID is required"}), 400

        print(f"🟢 Fetching profile for Specialist ID: {specialist_id}")

        # First raw check
        raw_check = fetch_data("SELECT * FROM health_specialist WHERE SpecialistID = %s", (specialist_id,))
        print("🔍 Raw specialist check:", raw_check)

        sql_query = """
        SELECT u.FullName, u.Email, h.Profession, h.Speciality, h.SpecialistID
        FROM health_specialist h
        JOIN users u ON h.UserID = u.UserID
        WHERE h.SpecialistID = %s
        """
        
        specialist_profile = fetch_data(sql_query, (specialist_id,))

        if not specialist_profile:
            print(f"❌ No profile found for Specialist ID: {specialist_id}")  # Debugging output
            return jsonify({"error": "No user profile found"}), 404

        return jsonify(specialist_profile), 200

    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/update_patient_profile', methods=['POST'])
def update_patient_profile():
    try:
        data = request.json
        patient_id = data.get("patient_id")
        full_name = data.get("full_name")
        gender = data.get("gender")
        age = data.get("age")
        email = data.get("email")
        contact = data.get("contact")

        if not patient_id:
            return jsonify({"error": "Patient ID is required"}), 400

        # **Update `users` table (Full Name & Email)**
        update_user_query = """
        UPDATE users 
        SET FullName = %s, Email = %s 
        WHERE UserID = (SELECT UserID FROM patients WHERE patientID = %s)
        """
        modify_data(update_user_query, (full_name, email, patient_id))

        # **Update `patients` table (Gender, Age, Contact)**
        update_patient_query = """
        UPDATE patients 
        SET Gender = %s, Age = %s, Contact = %s 
        WHERE patientID = %s
        """
        modify_data(update_patient_query, (gender, age, contact, patient_id))

        return jsonify({"message": "Profile updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/update_specialist_profile', methods=['POST'])
def update_specialist_profile():
    try:
        data = request.json
        specialist_id = data.get("specialist_id")
        full_name = data.get("full_name")
        email = data.get("email")
        profession = data.get("profession")
        speciality = data.get("speciality")

        if not specialist_id:
            return jsonify({"error": "Specialist ID is required"}), 400

        # ✅ Update FullName & Email in users table via UserID lookup
        update_user_query = """
        UPDATE users 
        SET FullName = %s, Email = %s 
        WHERE UserID = (SELECT UserID FROM health_specialist WHERE SpecialistID = %s)
        """
        modify_data(update_user_query, (full_name, email, specialist_id))

        # ✅ Update Profession & Speciality in health_specialist
        update_specialist_query = """
        UPDATE health_specialist 
        SET Profession = %s, Speciality = %s
        WHERE SpecialistID = %s
        """
        modify_data(update_specialist_query, (profession, speciality, specialist_id))

        return jsonify({"message": "Specialist profile updated successfully"}), 200

    except Exception as e:
        print(f"❌ Error updating specialist profile: {e}")
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/get_trusted_contacts', methods=['GET'])
def get_trusted_contacts():
    try:
        patient_id = request.args.get("patient_id")
        if not patient_id:
            return jsonify({"error": "Patient ID is required"}), 400

        print(f"🟢 Fetching trusted contacts for Patient ID: {patient_id}")

        sql_query = """
        SELECT ContactID, ContactName, ContactNumber
        FROM trusted_contacts
        WHERE PatientID = %s
        """
        contacts = fetch_all_data(sql_query, (patient_id,))

        if not contacts:
            print("⚠ No contacts found in the database.")
            return jsonify([]), 200  # Return an empty list instead of 404

        return jsonify(contacts), 200  # Always return a list

    except Exception as e:
        print(f"❌ Error fetching contacts: {e}")
        return jsonify({"error": "An error occurred"}), 500

@app.route('/add_trusted_contact', methods=['POST'])
def add_trusted_contact():
    try:
        data = request.json
        patient_id = data.get("patient_id")
        contact_name = data.get("contact_name")
        contact_number = data.get("contact_number")

        if not (patient_id and contact_name and contact_number):
            return jsonify({"error": "Missing required fields"}), 400

        query = "INSERT INTO trusted_contacts (PatientID, ContactName, ContactNumber) VALUES (%s, %s, %s)"
        modify_data(query, (patient_id, contact_name, contact_number))

        return jsonify({"message": "Contact added successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/update_trusted_contact', methods=['POST'])
def update_trusted_contact():
    try:
        data = request.json
        contact_id = data.get("contact_id")
        contact_name = data.get("contact_name")
        contact_number = data.get("contact_number")

        if not (contact_id and contact_name and contact_number):
            return jsonify({"error": "Missing required fields"}), 400

        query = "UPDATE trusted_contacts SET ContactName = %s, ContactNumber = %s WHERE ContactID = %s"
        modify_data(query, (contact_name, contact_number, contact_id))

        return jsonify({"message": "Contact updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/delete_trusted_contact', methods=['POST'])
def delete_trusted_contact():
    try:
        data = request.json
        contact_id = data.get("contact_id")

        if not contact_id:
            return jsonify({"error": "Contact ID is required"}), 400

        query = "DELETE FROM trusted_contacts WHERE ContactID = %s"
        modify_data(query, (contact_id,))

        return jsonify({"message": "Contact deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

#MySQL + Firestore
@app.route('/sensor', methods=['POST'])
def receive_sensor_data():
    try:
        data = request.json
        ecg = data.get("ecg")
        respiration = data.get("respiration")
        temperature = data.get("temperature")

        # Input validation
        if None in [ecg, respiration, temperature]:
            return jsonify({"error": "All fields (ecg, respiration, temperature) are required."}), 400

        # Fetch active SmartShirt (ShirtStatus = 1 means connected)
        sql_query = """
        SELECT smartshirt.patientID, smartshirt.smartshirtID 
        FROM smartshirt 
        WHERE smartshirt.ShirtStatus = 1 
        LIMIT 1
        """
        result = fetch_data(sql_query)

        if not result:
            return jsonify({"error": "No active SmartShirt found."}), 404

        patient_id = result["patientID"]
        smartshirt_id = result["smartshirtID"]

        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        # Sensor Data
        sensor_data = {
            "timestamp": timestamp,
            "ecg": ecg,
            "respiration": respiration,
            "temperature": temperature,
            "patientID": patient_id,
            "smartshirtID": smartshirt_id
        }

        # Firebase (Real-time)
        insert_data("health_vitals", sensor_data)

        # MySQL (Permanent)
        sql_insert = """
        INSERT INTO health_vitals (timestamp, ecg, respiration_rate, temperature, patientID, smartshirtID) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        modify_data(sql_insert, (timestamp, ecg, respiration, temperature, patient_id, smartshirt_id))

        return jsonify({"status": "success", "data": sensor_data}), 200

    except Exception as e:
        print(f"❌ Error in /sensor API: {e}")
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/get_sensor', methods=['GET'])
def get_sensor_data():
    try:
        patient_id = request.args.get("patient_id")

        if not patient_id:
            return jsonify({"error": "Patient ID is required"}), 400

        # **Fetch latest data from Firestore**
        latest_data = fetch_latest_data("health_vitals", "patientID", patient_id)

        if not latest_data:
            return jsonify({"error": "No sensor data found for this patient"}), 404

        return jsonify(latest_data), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
    
# Specialist adds a patient by Patient ID (shortened UUID form)
@app.route('/specialist/add_patient', methods=['POST'])
def add_patient_to_specialist():
    data = request.json
    try:
        specialist_id = data['SpecialistID']  # From logged-in specialist context or request
        short_patient_id = data['PatientID'].lower()  # e.g., "804dc24d-ec75"

        # ✅ Correcting to use PatientID column, not UUID
        sql_patient_lookup = """
        SELECT PatientID FROM patients 
        WHERE LOWER(SUBSTRING(PatientID, 1, 13)) = %s
        """
        patient = fetch_data(sql_patient_lookup, (short_patient_id,))

        if not patient:
            return jsonify({"message": "Patient not found"}), 404

        patient_id = patient['PatientID']

        # Step 2: Insert into bridge table
        sql_add_relation = """
        INSERT INTO Patient_Specialist (SpecialistID, PatientID)
        VALUES (%s, %s)
        """
        modify_data(sql_add_relation, (specialist_id, patient_id))

        return jsonify({"message": "Patient successfully added!"}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while adding the patient."}), 500

@app.route('/specialist/patients/<specialist_id>', methods=['GET'])
def get_specialist_patients(specialist_id):
    try:
        sql = """
        SELECT 
            p.PatientID, 
            u.FullName, 
            u.Email
        FROM Patient_Specialist ps
        JOIN patients p ON ps.PatientID = p.PatientID
        JOIN users u ON p.UserID = u.UserID
        WHERE ps.SpecialistID = %s
        ORDER BY ps.HSP_Relation_ID DESC
        """
        patients = fetch_all_data(sql, (specialist_id,))
        return jsonify({"patients": patients}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch patients: {e}"}), 500

@app.route('/patient_insights/<patient_id>', methods=['GET'])
def get_patient_insights(patient_id):
    try:
        # Check if patient exists
        sql_patient_check = "SELECT * FROM patients WHERE PatientID = %s"
        patient_exists = fetch_data(sql_patient_check, (patient_id,))

        if not patient_exists:
            return jsonify({"error": "Patient not found"}), 404

        # Fetch latest health vitals
        sql_vitals = """
        SELECT 
            respiration_rate, 
            temperature, 
            ecg, 
            timestamp
        FROM health_vitals 
        WHERE patientID = %s 
        ORDER BY timestamp DESC 
        LIMIT 1
        """
        vitals = fetch_data(sql_vitals, (patient_id,))

        # Fetch basic patient profile (like gender, age, weight)
        sql_profile = """
        SELECT 
            p.Gender, 
            p.Age, 
            u.FullName 
        FROM patients p
        JOIN users u ON p.UserID = u.UserID
        WHERE p.PatientID = %s
        """
        profile = fetch_data(sql_profile, (patient_id,))

        if not profile:
            return jsonify({"error": "Patient profile not found"}), 404

        # ✅ Format timestamp to ISO 8601 if exists
        last_updated = None
        if vitals and vitals.get('timestamp'):
            try:
                # Parse SQL timestamp
                raw_timestamp = vitals.get('timestamp')
                dt_object = datetime.strptime(str(raw_timestamp), '%Y-%m-%d %H:%M:%S.%f')
                # Convert to ISO 8601
                last_updated = dt_object.isoformat()  # "2025-03-01T20:27:13.000"
            except Exception as e:
                print(f"Timestamp format issue: {e}")
                last_updated = None

        # Prepare final response
        response = {
            "FullName": profile.get("FullName", "Unknown"),
            "Gender": profile.get("Gender", "N/A"),
            "Age": profile.get("Age", "N/A"),
            # "Weight": profile.get("Weight", "N/A"),  # Add back if needed
            "respiration_rate": vitals.get("respiration_rate") if vitals else "N/A",
            "temperature": vitals.get("temperature") if vitals else "N/A",
            "ecg": vitals.get("ecg") if vitals else "N/A",
            "last_updated": last_updated if last_updated else None
        }
        print(response)

        return jsonify(response), 200

    except Exception as e:
        print(f"❌ Error fetching patient insights: {e}")
        return jsonify({"error": f"An error occurred: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) 