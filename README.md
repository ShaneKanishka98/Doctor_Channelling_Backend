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
  - **Body**: `{"name": "John Doe", "email": "john@example.com", "password": "pass123", "role": "patient"}`
  - **Response**: `201` - `{"message": "User registered successfully", "user_id": 1}`

- **POST /login**
  - Logs in a user and returns a JWT token.
  - **Body**: `{"email": "john@example.com", "password": "pass123"}`
  - **Response**: `200` - `{"token": "jwt_token_here", "role": "patient"}`

### Appointments (Requires Token)
- **GET /appointments**
  - Lists all appointments.
  - **Header**: `Authorization: Bearer <token>`
  - **Response**: `200` - `{"appointments": [[1, 1, "John Doe", 1, "2025-03-04", "10:00"]]}`

- **GET /appointments/<id>**
  - Gets one appointment by ID.
  - **Header**: `Authorization: Bearer <token>`
  - **Response**: `200` - `{"appointment": [1, 1, "John Doe", 1, "2025-03-04", "10:00"]}`

- **POST /appointments** (Admin Only)
  - Creates a new appointment.
  - **Header**: `Authorization: Bearer <token>`
  - **Body**: `{"doctor_id": 1, "patient_name": "John Doe", "patient_id": 1, "date": "2025-03-04", "time": "10:00"}`
  - **Response**: `201` - `{"message": "Appointment created successfully", "appointment_id": 1}`

- **PUT /appointments/<id>** (Admin Only)
  - Updates an appointment.
  - **Header**: `Authorization: Bearer <token>`
  - **Body**: `{"doctor_id": 1, "patient_name": "Jane Doe", "patient_id": 1, "date": "2025-03-05", "time": "14:00"}`
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
  - **Response**: `200` - `{"patients": [[1, "John Doe", "john@example.com", "hashed_password", "patient"]]}`

- **DELETE /patients/<id>** (Admin Only)
  - Deletes a patient.
  - **Header**: `Authorization: Bearer <token>`
  - **Response**: `200` - `{"message": "Patient deleted successfully"}`

---

## Testing the API
1. Use **Postman** or **curl** to test endpoints.
2. **Steps**:
   - Register a user (`/signup`).
   - Log in (`/login`) to get a token.
   - Add the token to the `Authorization` header as `Bearer <token>` for protected routes.
3. **Example with curl**:
   ```bash
   curl -X POST http://localhost:5000/signup -H "Content-Type: application/json" -d '{"name":"John Doe","email":"john@example.com","password":"pass123","role":"patient"}'
   ```

---

## Notes
- **Security**: Don’t use `debug=True` in production; it exposes errors.
- **Database**: Ensure PostgreSQL is running and credentials match your `.env` file.
- **Admin Access**: Register an admin user (`role: "admin"`) to manage appointments, doctors, and patients.
