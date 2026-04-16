from database.connection import get_connection
from services.logger import logger


class BankingService:

    def __init__(self, customer_repo, account_repo, transaction_repo):
        self.customer_repo = customer_repo
        self.account_repo = account_repo
        self.transaction_repo = transaction_repo

    # -----------------------------
    # Deposit
    # -----------------------------
    def deposit(self, user_id: int, account_number: str, amount: float):

        # 1️⃣ Validate amount
        if amount <= 0:
            raise Exception("Invalid amount")

        conn = get_connection()
        try:
            cursor = conn.cursor()

            # 2️⃣ Ownership check
            cursor.execute("""
                SELECT id, balance FROM accounts
                WHERE account_number = %s AND customer_id = %s
            """, (account_number, user_id))

            account = cursor.fetchone()

            if not account:
                raise Exception("Unauthorized account access")

            current_balance = account["balance"]

            # 3️⃣ Calculate new balance
            new_balance = current_balance + amount

            # 4️⃣ Update balance
            cursor.execute("""
                UPDATE accounts
                SET balance = %s
                WHERE account_number = %s
            """, (new_balance, account_number))

            # 5️⃣ Log transaction with balance_after ✅
            cursor.execute("""
                INSERT INTO transactions (
                    account_id,
                    amount,
                    transaction_type,
                    balance_after
                )
                VALUES (%s, %s, 'DEPOSIT', %s)
            """, (account["id"], amount, new_balance))

            conn.commit()

            return new_balance

        finally:
            conn.close()

    # -----------------------------
    # Withdraw
    # -----------------------------
    def withdraw(self, user_id: int, account_number: str, amount: float):

        # 1️⃣ Validate amount
        if amount <= 0:
            raise Exception("Invalid amount")

        conn = get_connection()
        try:
            cursor = conn.cursor()

            # 2️⃣ Ownership check
            cursor.execute("""
                SELECT id, balance FROM accounts
                WHERE account_number = %s AND customer_id = %s
            """, (account_number, user_id))

            account = cursor.fetchone()

            if not account:
                raise Exception("Unauthorized account access")

            current_balance = account["balance"]

            # 3️⃣ Balance check
            if current_balance < amount:
                raise Exception("Insufficient funds")

            new_balance = current_balance - amount

            # 4️⃣ Update balance
            cursor.execute("""
                UPDATE accounts
                SET balance = %s
                WHERE account_number = %s
            """, (new_balance, account_number))

            # 5️⃣ Log transaction (WITH balance_after ✅)
            cursor.execute("""
                INSERT INTO transactions (account_id, amount, transaction_type, balance_after)
                VALUES (%s, %s, 'WITHDRAW', %s)
            """, (account["id"], amount, new_balance))

            conn.commit()

            return new_balance

        finally:
            conn.close()

    # -----------------------------
    # Transfer (Atomic)
    # -----------------------------
    def transfer(self, user_id: int, sender_acc: str, receiver_acc: str, amount: float):

        # 1️⃣ Basic validations
        if amount <= 0:
            raise Exception("Invalid amount")

        if sender_acc == receiver_acc:
            raise Exception("Cannot transfer to same account")

        conn = get_connection()
        try:
            cursor = conn.cursor()

            # 2️⃣ Lock sender row (prevents race condition 🔥)
            cursor.execute("""
                SELECT id, balance FROM accounts
                WHERE account_number = %s AND customer_id = %s
                FOR UPDATE
            """, (sender_acc, user_id))

            sender = cursor.fetchone()

            if not sender:
                raise Exception("Unauthorized sender account")

            # 3️⃣ Lock receiver row
            cursor.execute("""
                SELECT id, balance FROM accounts
                WHERE account_number = %s
                FOR UPDATE
            """, (receiver_acc,))

            receiver = cursor.fetchone()

            if not receiver:
                raise Exception("Receiver not found")

            # 4️⃣ Balance check
            if sender["balance"] < amount:
                raise Exception("Insufficient funds")

            # 5️⃣ Calculate balances
            new_sender_balance = sender["balance"] - amount
            new_receiver_balance = receiver["balance"] + amount

            # 6️⃣ Update sender
            cursor.execute("""
                UPDATE accounts
                SET balance = %s
                WHERE id = %s
            """, (new_sender_balance, sender["id"]))

            # 7️⃣ Update receiver
            cursor.execute("""
                UPDATE accounts
                SET balance = %s
                WHERE id = %s
            """, (new_receiver_balance, receiver["id"]))

            # 8️⃣ Generate reference (optional but 🔥)
            reference = f"TXN-{sender_acc[-4:]}-{receiver_acc[-4:]}"

            # 9️⃣ Log sender transaction
            cursor.execute("""
                INSERT INTO transactions (
                    account_id,
                    amount,
                    transaction_type,
                    balance_after,
                    reference
                )
                VALUES (%s, %s, 'TRANSFER_OUT', %s, %s)
            """, (
                sender["id"],
                amount,
                new_sender_balance,
                f"To {receiver_acc} | {reference}"
            ))

            # 🔟 Log receiver transaction
            cursor.execute("""
                INSERT INTO transactions (
                    account_id,
                    amount,
                    transaction_type,
                    balance_after,
                    reference
                )
                VALUES (%s, %s, 'TRANSFER_IN', %s, %s)
            """, (
                receiver["id"],
                amount,
                new_receiver_balance,
                f"From {sender_acc} | {reference}"
            ))

            conn.commit()

            return {
                "sender_balance": new_sender_balance,
                "receiver_balance": new_receiver_balance,
                "reference": reference
            }

        except Exception as e:
            conn.rollback()  # 🔐 rollback everything if anything fails
            raise e

        finally:
            conn.close()

    # -----------------------------
    # Get Accounts by Customer
    # -----------------------------
    def get_my_accounts(self, customer_id: int):
        return self.account_repo.get_accounts_by_customer(customer_id)

    # -----------------------------
    # Get Transactions by Account
    # -----------------------------
    def get_account_transactions(self, account_id: int):
        return self.transaction_repo.get_transactions_by_account(account_id)
