# Eve Healthcare - Diagnostic Booking API

A robust, production-ready backend RESTful API built with **FastAPI** and **PostgreSQL** that facilitates diagnostic test scheduling, centre management, and simulated payment processing.

This project demonstrates secure user authentication, complex relational database modeling, and handling distributed system edge cases such as webhook idempotency and database race conditions.

## 🚀 Key Features

- **JWT-Based Authentication:** Secure user signup and login using bcrypt password hashing and OAuth2 bearer tokens.
- **Entity Management:** Many-to-many database relationships connecting Diagnostic Centres with available Diagnostic Tests.
- **Secure Booking Engine:** Prevents client-side price tampering by resolving test prices server-side, validating centre test availability, and managing future-dated appointments.
- **Idempotent Payment Webhooks:** Simulates a payment gateway integration using database row-level locking (`with_for_update()`) and event ID tracking to prevent duplicate processing, race conditions, and double-charging during network retries.
- **Automated Test Suite:** Comprehensive test coverage using `pytest` and an isolated, ephemeral SQLite database to ensure data integrity without polluting the production database.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| **FastAPI** | REST API framework |
| **PostgreSQL** | Production database |
| **SQLite** | Testing database |
| **SQLAlchemy** | ORM and database interaction |
| **Pydantic V2** | Data validation and serialization |
| **PyJWT** | JWT token generation and validation |
| **Passlib / Bcrypt** | Secure password hashing |
| **Pytest** | Automated testing |
| **HTTPX** | API testing |

## 📂 Project Architecture

```text
eve-healthcare-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Environment settings
│   │   ├── database.py          # Database connection and session
│   │   └── security.py          # JWT and password hashing
│   ├── dependencies/
│   │   ├── __init__.py
│   │   └── auth.py              # Reusable authentication dependencies
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # User model
│   │   ├── diagnostic_test.py   # Diagnostic test model
│   │   ├── centre.py            # Diagnostic centre model
│   │   ├── booking.py           # Booking model
│   │   ├── payment.py           # Payment model
│   │   └── webhook_event.py     # Webhook event model
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── tests.py             # Diagnostic test endpoints
│   │   ├── centres.py           # Centre endpoints
│   │   ├── bookings.py          # Booking endpoints
│   │   └── payments.py          # Payment endpoints
│   └── schemas/
│       ├── __init__.py
│       ├── auth.py              # Authentication schemas
│       ├── tests.py             # Diagnostic test schemas
│       ├── centres.py           # Centre schemas
│       ├── bookings.py          # Booking schemas
│       └── payments.py          # Payment schemas
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Test fixtures
│   ├── test_auth.py
│   ├── test_bookings.py
│   └── test_payments.py
├── .env                         # Environment variables
├── requirements.txt             # Python dependencies
└── README.md
```

## ⚙️ How to Run This Project

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd eve-healthcare-backend
```

### 2. Create a Virtual Environment

#### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres:<your_password>@localhost:5432/eve_healthcare
SECRET_KEY=your-super-secret-jwt-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Make sure PostgreSQL is running and the `eve_healthcare` database exists.

### 5. Run the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

### 6. Open API Documentation

FastAPI automatically provides interactive API documentation:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### 7. Run Automated Tests

```bash
pytest -v
```

The test suite uses an isolated SQLite database so that tests do not modify the production PostgreSQL database.

---

# 🔐 API Endpoints

| Endpoint | Method | Description | Authentication |
|---|---|---|---|
| `/auth/signup` | POST | Register a new user | No |
| `/auth/login` | POST | Authenticate and receive JWT | No |
| `/tests` | POST | Create a diagnostic test | Yes |
| `/centres` | POST | Create a centre and link tests | Yes |
| `/bookings/` | POST | Book a diagnostic test | Yes |
| `/payments/` | POST | Initiate a simulated payment | Yes |
| `/payments/webhook/` | POST | Process payment gateway status updates | No |

---

# 📡 Example API Requests

## 1. User Signup

**POST** `/auth/signup`

```json
{
  "name": "Parineet Kakde",
  "email": "parineet@example.com",
  "password": "securepassword123"
}
```

---

## 2. User Login

**POST** `/auth/login`

```json
{
  "email": "parineet@example.com",
  "password": "securepassword123"
}
```

The API returns a JWT access token. Use the token in subsequent authenticated requests:

```http
Authorization: Bearer <your_access_token>
```

---

## 3. Create a Booking

**POST** `/bookings/`

Requires JWT authorization.

```json
{
  "centre_id": 1,
  "test_id": 1,
  "appointment_time": "2026-10-15T10:30:00Z"
}
```

### Booking Flow

```text
Client Request
      ↓
Validate JWT
      ↓
Validate Centre
      ↓
Validate Test
      ↓
Check Centre-Test Availability
      ↓
Fetch Price From Database
      ↓
Create Booking
      ↓
Return Booking Details
```

The booking amount is calculated from the server-side diagnostic test price rather than trusting a price supplied by the client.

---

## 4. Simulate Payment

**POST** `/payments/`

```json
{
  "booking_id": 1,
  "simulate_status": "PENDING"
}
```

This creates a simulated payment transaction associated with the booking.

---

## 5. Idempotent Payment Webhook

**POST** `/payments/webhook/`

```json
{
  "event_id": "evt_001",
  "transaction_ref": "pay_a1b2c3d4",
  "status": "SUCCESS"
}
```

The `event_id` is stored in the database.

If the same webhook is received again:

```text
Gateway
   │
   ├── evt_001 → Processed
   │
   └── evt_001 → Duplicate → Skipped
```

This prevents duplicate payment processing when payment providers retry webhook requests.

---

# 🗄️ Database / Schema Design

The application uses **PostgreSQL** with **SQLAlchemy ORM**.

## Users

Stores user profiles and securely hashed credentials.

```text
User
├── id
├── name
├── email
├── password_hash
└── created_at
```

Passwords are never stored as plain text. They are hashed using bcrypt.

---

## Diagnostic Centres & Tests

Diagnostic centres and tests have a **many-to-many relationship**.

```text
Diagnostic Centre
       │
       │ Many-to-Many
       │
       ▼
centre_test_association
       ▲
       │
       │
Diagnostic Test
```

A centre can offer multiple diagnostic tests, and a diagnostic test can be available at multiple centres.

---

## Bookings

A booking connects:

- User
- Diagnostic Centre
- Diagnostic Test

It also stores:

- Appointment time
- Server-calculated amount
- Booking status

Example booking statuses:

```text
PENDING
CONFIRMED
CANCELLED
```

---

## Payments

Payments are linked to bookings and track:

- Transaction reference
- Payment status
- Payment timestamps

---

## Payment Webhook Events

Webhook event IDs are stored to guarantee idempotency.

```text
Payment Gateway
      │
      ▼
Webhook Request
      │
      ▼
Check event_id
      │
 ┌────┴────┐
 │         │
Exists   New Event
 │         │
Skip      Lock Payment
           │
           ▼
      Update Payment
           │
           ▼
       Save Event
```

This protects the system against duplicate webhook requests and race conditions.

---

# 🔒 Security

The API implements several security measures:

### Password Hashing

User passwords are hashed using bcrypt before being stored in the database.

### JWT Authentication

Authenticated endpoints require an OAuth2 bearer token:

```http
Authorization: Bearer <access_token>
```

### Server-Side Price Validation

The client does not control the booking price. The backend retrieves the diagnostic test price directly from the database.

### Input Validation

Pydantic V2 schemas validate incoming request data before it reaches the application logic.

### Webhook Idempotency

Payment webhook events are tracked using unique event IDs to prevent duplicate processing.

---

# 🧪 Automated Testing

Run the complete test suite with:

```bash
pytest -v
```

The tests use an isolated SQLite database.

This allows the application to test:

- User registration
- Authentication
- JWT authorization
- Diagnostic test creation
- Centre creation
- Centre-test relationships
- Booking validation
- Server-side price calculation
- Payment creation
- Payment webhook processing
- Duplicate webhook handling

Example:

```text
tests/
├── conftest.py
├── test_auth.py
├── test_bookings.py
└── test_payments.py
```

The production PostgreSQL database is not used by the test suite.

---

# 💳 Payment Webhook Idempotency

One of the important parts of this project is handling duplicate payment webhooks.

Payment gateways can retry webhook requests if they do not receive a successful response quickly enough.

For example:

```text
Request 1:
event_id = evt_001
status = SUCCESS

Request 2:
event_id = evt_001
status = SUCCESS
```

Without idempotency, the application could process the payment twice.

The application prevents this by:

1. Checking whether the event ID has already been processed.
2. Locking the relevant database row using SQLAlchemy's `with_for_update()`.
3. Processing the payment only once.
4. Recording the webhook event.
5. Ignoring subsequent requests with the same event ID.

This design helps protect against race conditions and duplicate payment processing.

> **Production note:** PostgreSQL row-level locking is used for production payment processing. SQLite is used only for the automated test environment and does not provide identical concurrency semantics.

---

# 🔄 Booking & Payment Flow

The overall application flow is:

```text
                 ┌──────────────────┐
                 │      User        │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Authentication   │
                 │   JWT Login      │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Select Centre    │
                 │   & Test        │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Create Booking   │
                 │ Server Price     │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Initiate Payment │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Payment Gateway  │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Webhook Handler  │
                 │ Idempotent       │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Update Booking   │
                 │ / Payment Status │
                 └──────────────────┘
```

---

# 🧩 Future Improvements

## Dockerization

Add a `Dockerfile` and `docker-compose.yml` to containerize:

- FastAPI application
- PostgreSQL database

This would make local setup and deployment more consistent across environments.

## Role-Based Access Control

Implement roles such as:

```text
ADMIN
USER
```

Admins could manage diagnostic tests and centres, while standard users could book available tests.

## Redis Caching

Integrate Redis to cache frequently requested data such as:

- Available diagnostic centres
- Diagnostic tests
- Centre-test availability

This can reduce database load for high-frequency read requests.

## Pagination & Filtering

Add query parameters to booking endpoints, for example:

```http
GET /bookings/?status=CONFIRMED
GET /bookings/?from_date=2026-10-01&to_date=2026-10-31
```

This would make the API easier to integrate with frontend applications and admin dashboards.

---

# 📌 Project Highlights

This project focuses on backend engineering concepts including:

- REST API development
- FastAPI application architecture
- PostgreSQL relational database design
- SQLAlchemy ORM
- JWT authentication
- Password hashing
- Pydantic validation
- Many-to-many relationships
- Transaction management
- Database row-level locking
- Webhook idempotency
- Race-condition handling
- Automated API testing
- Production-oriented backend design

---

# 👨‍💻 Author

**Parineet Kakde**

B.Tech Computer Science Engineering

Built as a backend engineering project demonstrating secure authentication, relational database design, booking workflows, simulated payments, and reliable webhook processing.
