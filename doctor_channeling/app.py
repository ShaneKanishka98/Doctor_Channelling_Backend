import os  # Used to interact with the operating system (e.g., environment variables)
import jwt  # Library for creating and verifying JSON Web Tokens (JWT) for authentication
import datetime  # Helps manage dates and times, like token expiration
import psycopg2  # Connects to PostgreSQL database
from flask import Flask, request, jsonify  # Flask for building the API, request for handling HTTP requests, jsonify for JSON responses
from flask_bcrypt import Bcrypt  # Secures passwords by hashing them
from functools import wraps  # Helps create decorators (like for token checking)
from dotenv import load_dotenv  # Loads environment variables from a .env file

# Create the Flask app and set up password hashing
app = Flask(__name__)  # Initialize the Flask application
bcrypt = Bcrypt(app)  # Set up Bcrypt to hash passwords securely
load_dotenv()  # Load variables from .env file (like database credentials)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')  # Secret key for JWT; loaded from .env or defaults to 'your_secret_key'

# Database settings using environment variables or defaults
DB_PARAMS = {
    'dbname': os.getenv('DB_NAME', 'channel_db'),  # Database name (default: 'channel_db')
    'user': os.getenv('DB_USER', 'postgres'),  # Database user (default: 'postgres')
    'password': os.getenv('DB_PASSWORD', 'Shane@2618'),  # Database password (default: 'Shane@2618')
    'host': os.getenv('DB_HOST', 'localhost'),  # Database host (default: 'localhost')
    'port': os.getenv('DB_PORT', '5432')  # Database port (default: '5432')
}

# Function to connect to the database
def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_PARAMS)  # Try to connect to PostgreSQL with the settings
        return conn  # Return the connection if successful
    except Exception as e:
        print(f"Error connecting to the database: {e}")  # Print error if connection fails
        return None  # Return None if it fails

# Function to create database tables if they don’t exist
def create_tables():
    conn = get_db_connection()  # Get a database connection
    if not conn:  # If connection fails, stop here
        return
    cur = conn.cursor()  # Create a cursor to run SQL commands
    try:
        # Create 'users' table for storing user info
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,  -- Auto-incrementing ID for each user
                name VARCHAR(100) NOT NULL,  -- User’s name
                email VARCHAR(100) UNIQUE NOT NULL,  -- Unique email address
                password TEXT NOT NULL,  -- Hashed password
                role VARCHAR(50) CHECK (role IN ('admin', 'doctor', 'patient')) NOT NULL  -- User role (admin, doctor, or patient)
            );
        """)
        # Create 'doctor' table for doctor details
        cur.execute("""
            CREATE TABLE IF NOT EXISTS doctor (
                id SERIAL PRIMARY KEY,  -- Auto-incrementing ID for each doctor
                name VARCHAR(100) NOT NULL,  -- Doctor’s name
                specialization VARCHAR(100) NOT NULL,  -- Doctor’s specialty (e.g., Cardiology)
                available_days VARCHAR(100) NOT NULL  -- Days they’re available (e.g., "Mon, Wed, Fri")
            );
        """)
        # Create 'appointment' table for booking appointments
        cur.execute("""
            CREATE TABLE IF NOT EXISTS appointment (
                id SERIAL PRIMARY KEY,  -- Auto-incrementing ID for each appointment
                doctor_id INT REFERENCES doctor(id) ON DELETE CASCADE,  -- Links to doctor; deletes if doctor is removed
                patient_name VARCHAR(100) NOT NULL,  -- Name of the patient
                patient_id INT NOT NULL,  -- Patient’s ID (not linked as foreign key yet)
                date VARCHAR(10) NOT NULL,  -- Appointment date (e.g., "2025-03-04")
                time VARCHAR(5) NOT NULL  -- Appointment time (e.g., "10:00")
            );
        """)
        # Create 'logs' table to track user actions
        cur.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id SERIAL PRIMARY KEY,  -- Auto-incrementing ID for each log entry
                user_id INT,  -- ID of the user who did the action
                action VARCHAR(255) NOT NULL,  -- What they did (e.g., "User registered")
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- When it happened
            );
        """)
        conn.commit()  # Save all changes to the database
    except Exception as e:
        print(f"Error creating tables: {e}")  # Print error if table creation fails
    finally:
        cur.close()  # Close the cursor
        conn.close()  # Close the connection

create_tables()  # Run this when the app starts to set up tables

# Function to log what users do (e.g., "User registered")
def log_action(user_id, action):
    conn = get_db_connection()  # Get a database connection
    if not conn:  # If connection fails, stop here
        return
    cur = conn.cursor()  # Create a cursor for SQL commands
    try:
        cur.execute("INSERT INTO logs (user_id, action) VALUES (%s, %s);", (user_id, action))  # Add log entry
        conn.commit()  # Save the log to the database
    except Exception as e:
        print(f"Error logging action: {e}")  # Print error if logging fails
    finally:
        cur.close()  # Close the cursor
        conn.close()  # Close the connection

# Decorator to check if a valid JWT token is provided
def token_required(f):
    @wraps(f)  # Keeps the original function’s metadata
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')  # Get the token from the request header
        if not token:  # If no token is found
            return jsonify({'message': 'Token is missing'}), 401  # Return error
        try:
            token = token.split(" ")[1]  # Extract token part after "Bearer"
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])  # Decode the token
            request.user = data  # Attach user info (like ID and role) to the request
        except jwt.ExpiredSignatureError:  # If token is expired
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:  # If token is invalid
            return jsonify({'message': 'Token is invalid'}), 401
        except Exception as e:  # Any other token-related error
            return jsonify({'message': 'Token decoding error', 'error': str(e)}), 401
        return f(*args, **kwargs)  # Call the original function if token is valid
    return decorated

# Route to register a new user
@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()  # Get JSON data from the request (name, email, password, role)
        conn = get_db_connection()  # Connect to the database
        if not conn:  # If connection fails
            return jsonify({'message': 'Database connection failed'}), 500  # Return error
        cur = conn.cursor()  # Create a cursor for SQL
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')  # Hash the password
        cur.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s) RETURNING id;",
                    (data['name'], data['email'], hashed_password, data['role']))  # Add user to database
        user_id = cur.fetchone()[0]  # Get the new user’s ID
        conn.commit()  # Save changes
        log_action(user_id, "User registered")  # Log the action
        return jsonify({'message': 'User registered successfully', 'user_id': user_id}), 201  # Return success
    except Exception as e:
        return jsonify({'error': str(e)}), 400  # Return error if something goes wrong

# Route to log in a user and get a JWT token
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()  # Get JSON data (email, password)
        conn = get_db_connection()  # Connect to the database
        if not conn:  # If connection fails
            return jsonify({'message': 'Database connection failed'}), 500
        cur = conn.cursor()  # Create a cursor
        cur.execute("SELECT id, password, role FROM users WHERE email = %s;", (data['email'],))  # Find user by email
        user = cur.fetchone()  # Get user data
        if user and bcrypt.check_password_hash(user[1], data['password']):  # Check if user exists and password matches
            token = jwt.encode({'user_id': user[0], 'role': user[2], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)},
                               app.config['SECRET_KEY'], algorithm='HS256')  # Create a token that expires in 2 hours
            log_action(user[0], "User logged in")  # Log the login
            return jsonify({'token': token, 'role': user[2]})  # Return token and role
        return jsonify({'message': 'Invalid credentials'}), 401  # Return error if login fails
    except Exception as e:
        return jsonify({'error': str(e)}), 400  # Return error if something goes wrong

# Route to get all appointments (requires token)
@app.route('/appointments', methods=['GET'])
@token_required  # Check for valid token
def read_all_appointments():
    conn = get_db_connection()  # Connect to the database
    if not conn:  # If connection fails
        return jsonify({'message': 'Database connection failed'}), 500
    cur = conn.cursor()  # Create a cursor
    cur.execute("SELECT * FROM appointment;")  # Get all appointments
    appointments = cur.fetchall()  # Fetch all results
    cur.close()  # Close cursor
    conn.close()  # Close connection
    if not appointments:  # If no appointments are found
        return jsonify({'message': 'No appointments found'}), 404
    return jsonify({'appointments': appointments}), 200  # Return list of appointments

# Route to get a specific appointment by ID (requires token)
@app.route('/appointments/<int:id>', methods=['GET'])
@token_required
def read_appointment(id):
    conn = get_db_connection()  # Connect to the database
    if not conn:  # If connection fails
        return jsonify({'message': 'Database connection failed'}), 500
    cur = conn.cursor()  # Create a cursor
    cur.execute("SELECT * FROM appointment WHERE id = %s;", (id,))  # Find appointment by ID
    appointment = cur.fetchone()  # Get the result
    cur.close()  # Close cursor
    conn.close()  # Close connection
    if not appointment:  # If appointment isn’t found
        return jsonify({'message': 'Appointment not found'}), 404
    return jsonify({'appointment': appointment}), 200  # Return the appointment

# Route to create a new appointment (admin only, requires token)
@app.route('/appointments', methods=['POST'])
@token_required
def create_appointment():
    if request.user['role'] != 'admin':  # Check if user is an admin
        return jsonify({'message': 'Unauthorized'}), 403  # Return error if not admin
    data = request.get_json()  # Get JSON data (doctor_id, patient_name, etc.)
    conn = get_db_connection()  # Connect to the database
    if not conn:  # If connection fails
        return jsonify({'message': 'Database connection failed'}), 500
    cur = conn.cursor()  # Create a cursor
    cur.execute("INSERT INTO appointment (doctor_id, patient_name, patient_id, date, time) VALUES (%s, %s, %s, %s, %s) RETURNING id;",
                (data['doctor_id'], data['patient_name'], data['patient_id'], data['date'], data['time']))  # Add appointment
    appointment_id = cur.fetchone()[0]  # Get the new appointment’s ID
    conn.commit()  # Save changes
    log_action(request.user['user_id'], "Appointment created")  # Log the action
    cur.close()  # Close cursor
    conn.close()  # Close connection
    return jsonify({'message': 'Appointment created successfully', 'appointment_id': appointment_id}), 201  # Return success

# Route to update an appointment (admin only, requires token)
@app.route('/appointments/<int:id>', methods=['PUT'])
@token_required
def update_appointment(id):
    if request.user['role'] != 'admin':  # Check if user is an admin
        return jsonify({'message': 'Unauthorized'}), 403
    data = request.get_json()  # Get JSON data to update
    conn = get_db_connection()  # Connect to the database
    if not conn:  # If connection fails
        return jsonify({'message': 'Database connection failed'}), 500
    cur = conn.cursor()  # Create a cursor
    cur.execute("UPDATE appointment SET doctor_id = %s, patient_name = %s, patient_id = %s, date = %s, time = %s WHERE id = %s;",
                (data['doctor_id'], data['patient_name'], data['patient_id'], data['date'], data['time'], id))  # Update appointment
    conn.commit()  # Save changes
    log_action(request.user['user_id'], "Appointment updated")  # Log the action
    cur.close()  # Close cursor
    conn.close()  # Close connection
    return jsonify({'message': 'Appointment updated successfully'}), 200  # Return success

# Route to delete an appointment (admin only, requires token)
@app.route('/appointments/<int:id>', methods=['DELETE'])
@token_required
def delete_appointment(id):
    if request.user['role'] != 'admin':  # Check if user is an admin
        return jsonify({'message': 'Unauthorized'}), 403
    conn = get_db_connection()  # Connect to the database
    if not conn:  # If connection fails
        return jsonify({'message': 'Database connection failed'}), 500
    cur = conn.cursor()  # Create a cursor
    cur.execute("DELETE FROM appointment WHERE id = %s;", (id,))  # Delete the appointment
    conn.commit()  # Save changes
    cur.close()  # Close cursor
    conn.close()  # Close connection
    return jsonify({'message': 'Appointment deleted successfully'}), 200  # Return success

# Route to get all doctors (requires token)
@app.route('/doctors', methods=['GET'])
@token_required
def read_all_doctors():
    conn = get_db_connection()  # Connect to the database
    if not conn:  # If connection fails
        return jsonify({'message': 'Database connection failed'}), 500
    cur = conn.cursor()  # Create a cursor
    cur.execute("SELECT * FROM doctor;")  # Get all doctors
    doctors = cur.fetchall()  # Fetch all results
    cur.close()  # Close cursor
    conn.close()  # Close connection
    if not doctors:  # If no doctors are found
        return jsonify({'message': 'No doctors found'}), 404
    return jsonify({'doctors': doctors}), 200  # Return list of doctors

# Route to create a new doctor (admin only, requires token)
@app.route('/doctors', methods=['POST'])
@token_required
def create_doctor():
    if request.user['role'] != 'admin':  # Check if user is an admin
        return jsonify({'message': 'Unauthorized'}), 403
    data = request.get_json()  # Get JSON data (name, specialization, available_days)
    conn = get_db_connection()  # Connect to the database
    if not conn:  # If connection fails
        return jsonify({'message': 'Database connection failed'}), 500
    cur = conn.cursor()  # Create a cursor
    cur.execute("INSERT INTO doctor (name, specialization, available_days) VALUES (%s, %s, %s) RETURNING id;",
                (data['name'], data['specialization'], data['available_days']))  # Add doctor
    doctor_id = cur.fetchone()[0]  # Get the new doctor’s ID
    conn.commit()  # Save changes
    log_action(request.user['user_id'], "Doctor added")  # Log the action
    cur.close()  # Close cursor
    conn.close()  # Close connection
    return jsonify({'message': 'Doctor added successfully', 'doctor_id': doctor_id}), 201  # Return success

# Route to update a doctor (admin only, requires token)
@app.route('/doctors/<int:id>', methods=['PUT'])
@token_required
def update_doctor(id):
    if request.user['role'] != 'admin':  # Check if user is an admin
        return jsonify({'message': 'Unauthorized'}), 403
    data = request.get_json()  # Get JSON data to update
    conn = get_db_connection()  # Connect to the database
    if not conn:  # If connection fails
        return jsonify({'message': 'Database connection failed'}), 500
    cur = conn.cursor()  # Create a cursor
    cur.execute("UPDATE doctor SET name = %s, specialization = %s, available_days = %s WHERE id = %s;",
                (data['name'], data['specialization'], data['available_days'], id))  # Update doctor
    conn.commit()  # Save changes
    log_action(request.user['user_id'], "Doctor updated")  # Log the action
    cur.close()  # Close cursor
    conn.close()  # Close connection
    return jsonify({'message': 'Doctor updated successfully'}), 200  # Return success

# Route to delete a doctor (admin only, requires token)
@app.route('/doctors/<int:id>', methods=['DELETE'])
@token_required
def delete_doctor(id):
    if request.user['role'] != 'admin':  # Check if user is an admin
        return jsonify({'message': 'Unauthorized'}), 403
    conn = get_db_connection()  # Connect to the database
    if not conn:  # If connection fails
        return jsonify({'message': 'Database connection failed'}), 500
    cur = conn.cursor()  # Create a cursor
    cur.execute("DELETE FROM doctor WHERE id = %s;", (id,))  # Delete the doctor
    conn.commit()  # Save changes
    cur.close()  # Close cursor
    conn.close()  # Close connection
    return jsonify({'message': 'Doctor deleted successfully'}), 200  # Return success

# Route to get all patients (requires token)
@app.route('/patients', methods=['GET'])
@token_required
def read_all_patients():
    conn = get_db_connection()  # Connect to the database
    if not conn:  # If connection fails
        return jsonify({'message': 'Database connection failed'}), 500
    cur = conn.cursor()  # Create a cursor
    cur.execute("SELECT * FROM users WHERE role = 'patient';")  # Get all patients
    patients = cur.fetchall()  # Fetch all results
    cur.close()  # Close cursor
    conn.close()  # Close connection
    if not patients:  # If no patients are found
        return jsonify({'message': 'No patients found'}), 404
    return jsonify({'patients': patients}), 200  # Return list of patients

# Route to delete a patient (admin only, requires token)
@app.route('/patients/<int:id>', methods=['DELETE'])
@token_required
def delete_patient(id):
    if request.user['role'] != 'admin':  # Check if user is an admin
        return jsonify({'message': 'Unauthorized'}), 403
    conn = get_db_connection()  # Connect to the database
    if not conn:  # If connection fails
        return jsonify({'message': 'Database connection failed'}), 500
    cur = conn.cursor()  # Create a cursor
    cur.execute("DELETE FROM users WHERE id = %s;", (id,))  # Delete the patient
    conn.commit()  # Save changes
    cur.close()  # Close cursor
    conn.close()  # Close connection
    return jsonify({'message': 'Patient deleted successfully'}), 200  # Return success

# Start the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Run the app on port 5000; debug mode shows errors
