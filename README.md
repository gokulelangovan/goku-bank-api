# 🏦 Goku Bank API

A full-stack inspired backend banking system built using **FastAPI** and **PostgreSQL**, designed with clean architecture and real-world practices.

---

## 🚀 Features

* 🔐 **JWT Authentication**

  * User registration & login
  * Secure password hashing (bcrypt)

* 🏦 **Account Management**

  * Create multiple accounts per user
  * Unique account numbers

* 💸 **Transactions**

  * Deposit & Withdraw
  * Secure Transfer between accounts
  * Atomic transactions (rollback on failure)

* 📜 **Transaction History**

  * View all transactions per user
  * Ordered by latest activity

* 🧠 **Clean Architecture**

  * Routes → Services → Repositories
  * Separation of concerns
  * Scalable structure

---

## 🏗️ Tech Stack

* **Backend:** FastAPI
* **Database:** PostgreSQL
* **Auth:** JWT (python-jose)
* **ORM/DB Access:** psycopg2
* **Security:** bcrypt
* **Environment Management:** python-dotenv

---

## 📂 Project Structure

```
goku_bank/
│
├── database/
│   ├── connection.py
│   └── init_db.py
│
├── repositories/
│   ├── user_repository.py
│   ├── customer_repository.py
│   ├── account_repository.py
│   └── transaction_repository.py
│
├── services/
│   ├── auth_service.py
│   ├── banking_service.py
│   ├── jwt_handler.py
│   └── security.py
│
├── schemas/
│   ├── auth_schema.py
│   └── banking_schema.py
│
├── main.py
├── requirements.txt
└── .env
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/goku-bank-api.git
cd goku-bank-api
```

---

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3️⃣ Setup PostgreSQL

* Install PostgreSQL
* Create a database:

```sql
CREATE DATABASE goku_bank;
```

---

### 4️⃣ Configure environment variables

Create a `.env` file:

```
DATABASE_URL=postgresql://postgres:1234@localhost:5432/goku_bank
```

---

### 5️⃣ Run the server

```bash
uvicorn main:app --reload
```

---

### 6️⃣ Open API Docs

```
http://127.0.0.1:8000/docs
```

---

## 🧪 API Flow

1. Register user
2. Login → get JWT token
3. Create account
4. Deposit / Withdraw
5. Transfer funds
6. View transactions

---

## 🔐 Security Highlights

* Password hashing using bcrypt
* JWT-based authentication
* Ownership validation for transactions

---

## 🧠 Key Learnings

* Real-world debugging > tutorials
* Database schema must match application logic
* Environment configuration is critical
* Transaction safety is essential in financial systems

---

## 🚀 Future Improvements

* Add `transfer_id` for transaction linking
* Store `balance_after` for audit logs
* Role-based access (admin/user)
* Frontend integration (React)
* Deploy with Render + managed PostgreSQL

---

## 👨‍💻 Author

Built by Gokul 🚀
From CLI → Full Backend System

---

## ⭐ If you like this project

Give it a star ⭐ and share your thoughts!
