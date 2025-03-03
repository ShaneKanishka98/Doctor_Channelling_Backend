# Healthcare API

This is a simple RESTful API built with Flask to manage a healthcare system. It allows users to register, log in, and handle appointments, doctors, and patients. The app uses PostgreSQL for data storage, JWT for secure authentication, and Bcrypt for password hashing.

---

## Features
- Register and log in users with roles (admin, doctor, patient).
- Create, read, update, and delete appointments (admin only for changes).
- Manage doctors (admin only for adding/updating/deleting).
- View and delete patients (admin only for deletion).
- Log user actions (e.g., registration, login).

---

## Technologies Used
- **Python**: Backend language.
- **Flask**: Web framework for the API.
- **PostgreSQL**: Database to store data.
- **JWT**: Secure token-based authentication.
- **Bcrypt**: Password hashing for security.
- **python-dotenv**: Loads environment variables from a `.env` file.

---

## Setup

### Prerequisites
- Python 3.8 or higher.
- PostgreSQL installed and running.
- Postman (for testing the API).
- Git (to clone the project, optional).

### Installation
1. **Clone the Project** (if using Git):
   ```bash
   git clone https://github.com/yourusername/healthcare-api.git
   cd healthcare-api
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Required Libraries**:
   ```bash
   pip install flask flask-bcrypt psycopg2-binary pyjwt python-dotenv
   ```

### Database Setup
1. **Create a PostgreSQL Database**:
   - Open your PostgreSQL client (e.g., psql) and run:
     ```sql
     CREATE DATABASE channel_db;
     ```

2. **Set Environment Variables**:
   - Create a `.env` file in the project folder and add:
     ```
     DB_NAME=channel_db
     DB_USER=postgres
     DB_PASSWORD=your_password_here
     DB_HOST=localhost
     DB_PORT=5432
     SECRET_KEY=your_secret_key_here
     ```
   - Replace `your_password_here` with your PostgreSQL password and `your_secret_key_here` with a random, secure string (e.g., `python -c "import secrets; print(secrets.token_hex(16))"`).

3. **Tables Are Created Automatically**:
   - When you run the app, it creates tables for `users`, `doctor`, `appointment`, and `logs`.

### Running the App
1. **Activate the Virtual Environment** (if not already active):
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Start the Flask Server**:
   ```bash
   python app.py
   ```
   - The API will run at `http://localhost:5000`. Debug mode is on, so errors will show in the terminal.

---

## API Endpoints

### Authentication
- **POST /signup**
  - Registers a new user.
  - **Body**: `{"name": "Shane Kanishka", "email": "shane@example.com", "password": "pass123", "role": "patient"}`
  - **Response**: `201` - `{"message": "User registered successfully", "user_id": 1}`

- **POST /login**
  - Logs in a user and returns a JWT token.
  - **Body**: `{"email": "shane@example.com", "password": "pass123"}`
  - **Response**: `200` - `{"token": "jwt_token_here", "role": "patient"}`

### Appointments (Requires Token)
- **GET /appointments**
  - Lists all appointments.
  - **Header**: `Authorization: Bearer <token>`
  - **Response**: `200` - `{"appointments": [[1, 1, "Shane Kanishka", 1, "2025-03-04", "10:00"]]}`

- **GET /appointments/<id>**
  - Gets one appointment by ID.
  - **Header**: `Authorization: Bearer <token>`
  - **Response**: `200` - `{"appointment": [1, 1, "John Doe", 1, "2025-03-04", "10:00"]}`

- **POST /appointments** (Admin Only)
  - Creates a new appointment.
  - **Header**: `Authorization: Bearer <token>`
  - **Body**: `{"doctor_id": 1, "patient_name": "P1", "patient_id": 1, "date": "2025-03-04", "time": "10:00"}`
  - **Response**: `201` - `{"message": "Appointment created successfully", "appointment_id": 1}`

- **PUT /appointments/<id>** (Admin Only)
  - Updates an appointment.
  - **Header**: `Authorization: Bearer <token>`
  - **Body**: `{"doctor_id": 1, "patient_name": "P2", "patient_id": 1, "date": "2025-03-05", "time": "14:00"}`
  - **Response**: `200` - `{"message": "Appointment updated successfully"}`

- **DELETE /appointments/<id>** (Admin Only)
  - Deletes an appointment.
  - **Header**: `Authorization: Bearer <token>`
  - **Response**: `200` - `{"message": "Appointment deleted successfully"}`

### Doctors (Requires Token)
- **GET /doctors**
  - Lists all doctors.
  - **Header**: `Authorization: Bearer <token>`
  - **Response**: `200` - `{"doctors": [[1, "Dr. Smith", "Cardiology", "Mon, Wed, Fri"]]}`

- **POST /doctors** (Admin Only)
  - Adds a new doctor.
  - **Header**: `Authorization: Bearer <token>`
  - **Body**: `{"name": "Dr. Smith", "specialization": "Cardiology", "available_days": "Mon, Wed, Fri"}`
  - **Response**: `201` - `{"message": "Doctor added successfully", "doctor_id": 1}`

- **PUT /doctors/<id>** (Admin Only)
  - Updates a doctor.
  - **Header**: `Authorization: Bearer <token>`
  - **Body**: `{"name": "Dr. Smith", "specialization": "Neurology", "available_days": "Tue, Thu"}`
  - **Response**: `200` - `{"message": "Doctor updated successfully"}`

- **DELETE /doctors/<id>** (Admin Only)
  - Deletes a doctor.
  - **Header**: `Authorization: Bearer <token>`
  - **Response**: `200` - `{"message": "Doctor deleted successfully"}`

### Patients (Requires Token)
- **GET /patients**
  - Lists all patients.
  - **Header**: `Authorization: Bearer <token>`
  - **Response**: `200` - `{"patients": [[1, "Shane Kanishka", "shane@example.com", "hashed_password", "patient"]]}`

- **DELETE /patients/<id>** (Admin Only)
  - Deletes a patient.
  - **Header**: `Authorization: Bearer <token>`
  - **Response**: `200` - `{"message": "Patient deleted successfully"}`

---

## Testing with Postman

### Postman Setup
1. **Install Postman**: Download and install from [postman.com](https://www.postman.com/).
2. **Set Base URL**: Use `http://localhost:5000` as the base URL.
3. **Create an Environment**:
   - In Postman, click "Environments" > "Add".
   - Name it (e.g., "Healthcare API").
   - Add variables:
     - `base_url`: `http://localhost:5000`
     - `token`: Leave blank (will be set after login).

### Test Cases

#### 1. User Registration (`/signup`)
- **Method**: POST
- **URL**: `{{base_url}}/signup`
- **Headers**: `Content-Type: application/json`
- **Body** (raw, JSON):
  ```json
  {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "password": "password123",
    "role": "patient"
  }
  ```
- **Expected**: `201` - `{"message": "User registered successfully", "user_id": 1}`
- **Test**: Duplicate email should return `400`.

#### 2. User Login (`/login`)
- **Method**: POST
- **URL**: `{{base_url}}/login`
- **Headers**: `Content-Type: application/json`
- **Body** (raw, JSON):
  ```json
  {
    "email": "shane@example.com",
    "password": "password123"
  }
  ```
- **Tests Script** (in Postman’s "Tests" tab):
  ```javascript
  pm.test("Login successful", function () {
      pm.response.to.have.status(200);
      const response = pm.response.json();
      pm.environment.set("token", response.token);
  });
  ```
- **Expected**: `200` - `{"token": "jwt_token_here", "role": "patient"}`
- **Test**: Invalid credentials should return `401`.

#### 3. Get All Appointments (`/appointments`)
- **Method**: GET
- **URL**: `{{base_url}}/appointments`
- **Headers**: `Authorization: Bearer {{token}}`
- **Expected**: `200` - `{"appointments": [...]}` or `404` if empty.
- **Test**: No token should return `401`.

#### 4. Create Appointment (`/appointments`) - Admin Only
- **Method**: POST
- **URL**: `{{base_url}}/appointments`
- **Headers**: 
  - `Authorization: Bearer {{token}}`
  - `Content-Type: application/json`
- **Body** (raw, JSON):
  ```json
  {
    "doctor_id": 1,
    "patient_name": "P1",
    "patient_id": 1,
    "date": "2025-03-04",
    "time": "10:00"
  }
  ```
- **Expected**: `201` - `{"message": "Appointment created successfully", "appointment_id": 1}` (admin token required)
- **Test**: Non-admin token should return `403`.

#### 5. Update Appointment (`/appointments/<id>`) - Admin Only
- **Method**: PUT
- **URL**: `{{base_url}}/appointments/1`
- **Headers**: 
  - `Authorization: Bearer {{token}}`
  - `Content-Type: application/json`
- **Body** (raw, JSON):
  ```json
  {
    "doctor_id": 1,
    "patient_name": "P2",
    "patient_id": 1,
    "date": "2025-03-05",
    "time": "14:00"
  }
  ```
- **Expected**: `200` - `{"message": "Appointment updated successfully"}`
- **Test**: Non-admin token should return `403`.

#### 6. Delete Doctor (`/doctors/<id>`) - Admin Only
- **Method**: DELETE
- **URL**: `{{base_url}}/doctors/1`
- **Headers**: `Authorization: Bearer {{token}}`
- **Expected**: `200` - `{"message": "Doctor deleted successfully"}`
- **Test**: Non-admin token should return `403`.

### Notes
- Register an admin user (`role: "admin"`) to test admin-only endpoints.
- Save requests in a Postman Collection for easy reuse.
- Test edge cases like missing fields or invalid tokens.

---

## Notes
- **Security**: Don’t use `debug=True` in production; it exposes errors.
- **Database**: Ensure PostgreSQL is running and credentials match your `.env` file.
- **Admin Access**: Register an admin user to manage appointments, doctors, and patients.
