# Doctor Channeling Backend

This is a simple **Doctor Channeling Backend API** built using Flask and PostgreSQL. The API allows managing doctors and appointments.

## Features
- Add and retrieve doctors
- Schedule and retrieve appointments

## Prerequisites
Ensure you have the following installed:
- Python 3
- PostgreSQL
- `pip` (Python package manager)

## Installation

### 1. Clone the repository
```sh
git clone <repository_url>
cd Doctor_Channelling_Backend
```

### 2. Create and Activate a Virtual Environment
```sh
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies
```sh
pip install flask psycopg2
```

### 4. Configure Database
Create a PostgreSQL database:
```sql
CREATE DATABASE channel_db;
```
Update database credentials in the `DB_PARAMS` dictionary inside `app.py`:
```python
DB_PARAMS = {
    'dbname': 'channel_db',
    'user': 'postgres',
    'password': '<put_your_password_here>',
    'host': 'localhost',
    'port': '5432'
}
```

### 5. Run the Application
```sh
python app.py
```
The server will start at `http://127.0.0.1:5000`

## API Endpoints

### 1. Add a Doctor
**Endpoint:** `POST /doctors`

**Request JSON:**
```json
{
    "name": "Dr. John Doe",
    "specialization": "Cardiologist",
    "available_days": "Monday, Wednesday, Friday"
}
```
**Response JSON:**
```json
{
    "message": "Doctor added successfully",
    "doctor_id": 1
}
```

### 2. Get All Doctors
**Endpoint:** `GET /doctors`

**Response JSON:**
```json
[
    {
        "id": 1,
        "name": "Dr. John Doe",
        "specialization": "Cardiologist",
        "available_days": "Monday, Wednesday, Friday"
    }
]
```

### 3. Schedule an Appointment
**Endpoint:** `POST /appointments`

**Request JSON:**
```json
{
    "doctor_id": 1,
    "patient_name": "Alice Smith",
    "date": "2025-03-10",
    "time": "10:30"
}
```
**Response JSON:**
```json
{
    "message": "Appointment scheduled successfully",
    "appointment_id": 1
}
```

### 4. Get Appointments for a Specific Doctor
**Endpoint:** `GET /appointments/{doctor_id}`

**Example:** `GET /appointments/1`

**Response JSON:**
```json
[
    {
        "id": 1,
        "patient_name": "Alice Smith",
        "date": "2025-03-10",
        "time": "10:30"
    }
]
```

