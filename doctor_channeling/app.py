from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# Configure the PostgreSQL database connection
DB_PARAMS = {
    'dbname': 'channel_db',
    'user': 'postgres',
    'password': '<put_your_password_here>',
    'host': 'localhost',
    'port': '5432'
}

# Function to get database connection
def get_db_connection():
    return psycopg2.connect(**DB_PARAMS)

# Create tables if they don't exist
def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS doctor (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            specialization VARCHAR(100) NOT NULL,
            available_days VARCHAR(100) NOT NULL
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS appointment (
            id SERIAL PRIMARY KEY,
            doctor_id INT REFERENCES doctor(id) ON DELETE CASCADE,
            patient_name VARCHAR(100) NOT NULL,
            date VARCHAR(10) NOT NULL,
            time VARCHAR(5) NOT NULL
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

# Initialize database tables
create_tables()

# Route to get all doctors
@app.route('/doctors', methods=['GET'])
def get_doctors():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM doctor;")
    doctors = cur.fetchall()
    
    cur.close()
    conn.close()

    return jsonify([
        {'id': doc[0], 'name': doc[1], 'specialization': doc[2], 'available_days': doc[3]}
        for doc in doctors
    ])

# Route to add a new doctor
@app.route('/doctors', methods=['POST'])
def add_doctor():
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO doctor (name, specialization, available_days) VALUES (%s, %s, %s) RETURNING id;",
        (data['name'], data['specialization'], data['available_days'])
    )
    
    doctor_id = cur.fetchone()[0]
    conn.commit()
    
    cur.close()
    conn.close()
    
    return jsonify({'message': 'Doctor added successfully', 'doctor_id': doctor_id}), 201

# Route to schedule an appointment
@app.route('/appointments', methods=['POST'])
def schedule_appointment():
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO appointment (doctor_id, patient_name, date, time) VALUES (%s, %s, %s, %s) RETURNING id;",
        (data['doctor_id'], data['patient_name'], data['date'], data['time'])
    )

    appointment_id = cur.fetchone()[0]
    conn.commit()
    
    cur.close()
    conn.close()
    
    return jsonify({'message': 'Appointment scheduled successfully', 'appointment_id': appointment_id}), 201

# Route to get appointments for a specific doctor
@app.route('/appointments/<int:doctor_id>', methods=['GET'])
def get_appointments(doctor_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, patient_name, date, time FROM appointment WHERE doctor_id = %s;", (doctor_id,))
    appointments = cur.fetchall()

    cur.close()
    conn.close()
    
    return jsonify([
        {'id': appt[0], 'patient_name': appt[1], 'date': appt[2], 'time': appt[3]}
        for appt in appointments
    ])

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
