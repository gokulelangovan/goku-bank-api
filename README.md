# 🏦 Goku Bank API

A full-stack digital banking system built with **FastAPI + React**, featuring secure account management, transactions, and real-time balance tracking.

---

## 🚀 Features

### 🔐 Authentication
- JWT-based login system
- Secure user sessions

### 👤 Profile Management
- Update name & phone number
- Persistent user data

### 💳 Account System
- Multiple accounts per user
- Unique account numbers
- Real-time balance updates

### 💰 Transactions
- Deposit money
- Withdraw money
- Transfer between accounts

### 🔁 Transfer System (Secure)
- Ownership validation
- Receiver validation
- Insufficient balance protection
- Same-account transfer prevention
- Atomic DB transactions (no partial updates)
- Dual transaction logging (IN / OUT)

---

## 🧠 Security Highlights

- ❌ No unauthorized account access
- ❌ No negative or zero transactions
- ❌ No overdraft withdrawals
- ❌ No same-account transfers
- 🔐 Row-level locking using `FOR UPDATE`
- 🔁 Rollback on failure (data integrity guaranteed)

---

## 🛠 Tech Stack

### Backend
- FastAPI
- PostgreSQL
- Pydantic
- JWT Authentication

### Frontend
- React (Vite)
- Framer Motion
- React Hot Toast

---

## 📦 API Endpoints

### Auth
- `POST /login`

### Accounts
- `GET /accounts`

### Transactions
- `GET /transactions`

### Banking
- `POST /deposit`
- `POST /withdraw`
- `POST /transfer`

### Profile
- `PUT /update-profile`

---

## ⚙️ Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file:

```env
DATABASE_URL=your_db_url
SECRET_KEY=your_secret
```

Run the server:

```bash
uvicorn main:app --reload
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Sample Request

```bash
curl -X POST "http://127.0.0.1:8000/transfer" \
-H "Authorization: Bearer YOUR_TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "sender_account": "GBK-2026-000001",
  "receiver_account": "GBK-2026-000002",
  "amount": 1000
}'
```

---

## 📊 System Flow

```
User → JWT → Backend
     → Validate Ownership
     → Perform Transaction
     → Update Balance
     → Log Transaction
```

---

## 🔮 Future Improvements

- [ ] Transaction history filters
- [ ] Spending analytics dashboard
- [ ] External payment integration (UPI simulation)
- [ ] Rate limiting & fraud detection
- [ ] Admin panel

---

## 👨‍💻 Author

**Gokul 🐼** — Digital Associate @ Amazon

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!