from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

from database.connection import get_connection
from database.init_db import init_db

from schemas.banking_schema import (
    CreateAccountRequest,
    CreateAccountResponse,
    DepositRequest,
    WithdrawRequest,
    TransferRequest
)
from schemas.auth_schema import UserRegister
from schemas.auth_schema import UpdateProfileRequest

from services.auth_service import AuthService
from services.user_service import get_customer_id_by_user
from services.auth_dependency import get_current_user
from services.service_factory import get_banking_service

from repositories.customer_repository import CustomerRepository
from repositories.account_repository import AccountRepository

# -----------------------------
# APP
# -----------------------------
app = FastAPI(title="Goku Bank API 🚀")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

auth_service = AuthService()
customer_repo = CustomerRepository()
account_repo = AccountRepository()


# -----------------------------
# STARTUP — create tables if not exist
# -----------------------------
@app.on_event("startup")
def startup():
    init_db()


# -----------------------------
# ROOT
# -----------------------------
@app.get("/")
def home():
    return {"message": "Goku Bank API running 🚀"}


# -----------------------------
# REGISTER
# -----------------------------
@app.post("/register")
def register(user: UserRegister):
    try:
        user_id = auth_service.register_user(user.email, user.password)
        return {"message": "User created successfully", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------
# LOGIN
# -----------------------------
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        token = auth_service.login_user(form_data.username, form_data.password)
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------
# CREATE ACCOUNT
# -----------------------------
@app.post("/create-account", response_model=CreateAccountResponse)
def create_account(
    request: CreateAccountRequest,
    user_id: int = Depends(get_current_user)
):
    try:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT email FROM users WHERE id = %s",
                (user_id,)
            )
            user = cursor.fetchone()

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            email = user["email"]

            existing_customer = customer_repo.get_by_email(email)

            if existing_customer:
                customer_id = existing_customer["id"]
            else:
                customer_id = customer_repo.create_customer(
                    request.full_name,
                    email,
                    request.phone
                )

            cursor.execute(
                "UPDATE users SET customer_id = %s WHERE id = %s",
                (customer_id, user_id)
            )
            conn.commit()
        finally:
            conn.close()

        account_number = account_repo.create_account(
            customer_id,
            request.account_type
        )

        return {
            "message": "Account created successfully",
            "account_number": account_number
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------
# DEPOSIT
# -----------------------------
@app.post("/deposit")
def deposit(
    request: DepositRequest,
    service=Depends(get_banking_service),
    user_id: int = Depends(get_current_user)
):
    try:
        new_balance = service.deposit(
            user_id,
            request.account_number,
            request.amount
        )

        return {
            "message": "Deposit successful",
            "new_balance": new_balance
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# -----------------------------
# WITHDRAW
# -----------------------------
@app.post("/withdraw")
def withdraw(
    request: WithdrawRequest,
    service=Depends(get_banking_service),
    user_id: int = Depends(get_current_user)
):
    try:
        new_balance = service.withdraw(
            user_id,
            request.account_number,
            request.amount
        )

        return {
            "message": "Withdraw successful",
            "new_balance": new_balance
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------
# TRANSFER
# -----------------------------
@app.post("/transfer")
def transfer(
    request: TransferRequest,
    service=Depends(get_banking_service),
    user_id: int = Depends(get_current_user)
):
    try:
        result = service.transfer(
            user_id,
            request.sender_account,
            request.receiver_account,
            request.amount
        )

        return {
            "message": "Transfer successful",
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------
# MY ACCOUNTS
# -----------------------------
@app.get("/my-accounts")
def my_accounts(
    service=Depends(get_banking_service),
    user_id: int = Depends(get_current_user)
):
    try:
        customer_id = get_customer_id_by_user(user_id)

        if not customer_id:
            raise HTTPException(status_code=404, detail="Customer not found")

        customer = customer_repo.get_customer_by_id(customer_id)

        accounts = service.get_my_accounts(customer_id)

        return {
            "customer": {
                "name": customer["full_name"],
                "email": customer["email"],
                "phone": customer["phone"]
            },
            "accounts": [dict(a) for a in accounts]
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------
# MY TRANSACTIONS
# -----------------------------
@app.get("/my-transactions")
def my_transactions(
    service=Depends(get_banking_service),
    user_id: int = Depends(get_current_user)
):
    try:
        customer_id = get_customer_id_by_user(user_id)

        if not customer_id:
            raise HTTPException(status_code=404, detail="Customer not found")

        transactions = service.get_transactions(customer_id)

        return [dict(t) for t in transactions]

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------
# MY PROFILE
# -----------------------------
@app.get("/my-profile")
def my_profile(user_id: int = Depends(get_current_user)):
    try:
        customer_id = get_customer_id_by_user(user_id)

        if not customer_id:
            raise HTTPException(status_code=404, detail="Customer not found")

        customer = customer_repo.get_customer_by_id(customer_id)

        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        return dict(customer)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================
# ⭐ NEW: UPDATE PROFILE ROUTE
# =============================
@app.put("/update-profile")
def update_profile(
    request: UpdateProfileRequest,
    user_id: int = Depends(get_current_user)
):
    try:
        customer_id = get_customer_id_by_user(user_id)

        if not customer_id:
            raise HTTPException(status_code=404, detail="Customer not found")

        customer_repo.update_customer(
            customer_id,
            request.full_name,
            request.phone
        )

        return {"message": "Profile updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))