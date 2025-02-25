# Doctor Channelling Backend

A Flask-based REST API for doctor channeling, allowing patients to register, book appointments, and manage doctor availability. Built with PostgreSQL for database management.

## Features
- Add and retrieve doctor details
- Schedule and manage patient appointments
- PostgreSQL as the database
- Simple RESTful API endpoints

## Prerequisites
Make sure you have the following installed:
- Python (>=3.7)
- PostgreSQL (>=12)
- pip (Python package manager)

## Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-repo/Doctor_Channelling_Backend.git
cd Doctor_Channelling_Backend
```

### Step 2: Set Up a Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### Step 3: Install Required Dependencies
```bash
pip install flask psycopg2
```

### Step 4: Configure PostgreSQL Database
1. Create a PostgreSQL database:
   ```sql
   CREATE DATABASE channel_db;
   ```
2. Update the database credentials in `app.py`:
   ```python
   DB_PARAMS = {
       'dbname': 'channel_db',
       'user': 'postgres',
       'password': '<put_your_password_here>',
       'host': 'localhost',
       'port': '5432'
   }
   ```

### Step 5: Run the Application
```bash
python app.py
```

The application will start running on `http://0.0.0.0:5000/`.

## API Endpoints

### 1. Get All Doctors
**Endpoint:** `GET /doctors`
```bash
curl -X GET http://127.0.0.1:5000/doctors
```

### 2. Add a New Doctor
**Endpoint:** `POST /doctors`
```bash
curl -X POST http://127.0.0.1:5000/doctors \
     -H "Content-Type: application/json" \
     -d '{"name": "Dr. John Doe", "specialization": "Cardiology", "available_days": "Monday, Wednesday"}'
```

### 3. Schedule an Appointment
**Endpoint:** `POST /appointments`
```bash
curl -X POST http://127.0.0.1:5000/appointments \
     -H "Content-Type: application/json" \
     -d '{"doctor_id": 1, "patient_name": "Alice Smith", "date": "2025-02-25", "time": "10:30"}'
```

### 4. Get Appointments for a Specific Doctor
**Endpoint:** `GET /appointments/<doctor_id>`
```bash
curl -X GET http://127.0.0.1:5000/appointments/1
```
