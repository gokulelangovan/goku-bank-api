from database.connection import get_connection


class BankingService:

    def __init__(self, customer_repo, account_repo, transaction_repo):
        self.customer_repo = customer_repo
        self.account_repo = account_repo
        self.transaction_repo = transaction_repo

    # -----------------------------
    # Deposit
    # -----------------------------
    def deposit(self, user_id: int, account_number: str, amount: float):

        if amount <= 0:
            raise Exception("Invalid amount")

        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, balance FROM accounts
                WHERE account_number = %s AND customer_id = %s
            """, (account_number, user_id))

            account = cursor.fetchone()

            if not account:
                raise Exception("Unauthorized account access")

            new_balance = account["balance"] + amount

            cursor.execute("""
                UPDATE accounts
                SET balance = %s
                WHERE id = %s
            """, (new_balance, account["id"]))

            cursor.execute("""
                INSERT INTO transactions (account_id, amount, transaction_type, balance_after)
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

        if amount <= 0:
            raise Exception("Invalid amount")

        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, balance FROM accounts
                WHERE account_number = %s AND customer_id = %s
            """, (account_number, user_id))

            account = cursor.fetchone()

            if not account:
                raise Exception("Unauthorized account access")

            if account["balance"] < amount:
                raise Exception("Insufficient funds")

            new_balance = account["balance"] - amount

            cursor.execute("""
                UPDATE accounts
                SET balance = %s
                WHERE id = %s
            """, (new_balance, account["id"]))

            cursor.execute("""
                INSERT INTO transactions (account_id, amount, transaction_type, balance_after)
                VALUES (%s, %s, 'WITHDRAW', %s)
            """, (account["id"], amount, new_balance))

            conn.commit()
            return new_balance

        finally:
            conn.close()

    # -----------------------------
    # Transfer
    # -----------------------------
    def transfer(self, user_id: int, sender_acc: str, receiver_acc: str, amount: float):

        if amount <= 0:
            raise Exception("Invalid amount")

        if sender_acc == receiver_acc:
            raise Exception("Cannot transfer to same account")

        conn = get_connection()
        try:
            cursor = conn.cursor()

            # Lock sender
            cursor.execute("""
                SELECT id, balance FROM accounts
                WHERE account_number = %s AND customer_id = %s
                FOR UPDATE
            """, (sender_acc, user_id))

            sender = cursor.fetchone()

            if not sender:
                raise Exception("Unauthorized sender account")

            # Lock receiver
            cursor.execute("""
                SELECT id, balance FROM accounts
                WHERE account_number = %s
                FOR UPDATE
            """, (receiver_acc,))

            receiver = cursor.fetchone()

            if not receiver:
                raise Exception("Receiver not found")

            if sender["balance"] < amount:
                raise Exception("Insufficient funds")

            new_sender_balance = sender["balance"] - amount
            new_receiver_balance = receiver["balance"] + amount

            cursor.execute("""
                UPDATE accounts SET balance = %s WHERE id = %s
            """, (new_sender_balance, sender["id"]))

            cursor.execute("""
                UPDATE accounts SET balance = %s WHERE id = %s
            """, (new_receiver_balance, receiver["id"]))

            reference = f"TXN-{sender_acc[-4:]}-{receiver_acc[-4:]}"

            cursor.execute("""
                INSERT INTO transactions (account_id, amount, transaction_type, balance_after, reference)
                VALUES (%s, %s, 'TRANSFER_OUT', %s, %s)
            """, (sender["id"], amount, new_sender_balance, f"To {receiver_acc} | {reference}"))

            cursor.execute("""
                INSERT INTO transactions (account_id, amount, transaction_type, balance_after, reference)
                VALUES (%s, %s, 'TRANSFER_IN', %s, %s)
            """, (receiver["id"], amount, new_receiver_balance, f"From {sender_acc} | {reference}"))

            conn.commit()

            return {
                "sender_balance": new_sender_balance,
                "receiver_balance": new_receiver_balance,
                "reference": reference
            }

        except Exception as e:
            conn.rollback()
            raise e

        finally:
            conn.close()

    # -----------------------------
    # Get Accounts (FIXED)
    # -----------------------------
    def get_my_accounts(self, customer_id: int):
        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, account_number, balance, account_type
                FROM accounts
                WHERE customer_id = %s
            """, (customer_id,))

            return cursor.fetchall()

        finally:
            conn.close()

    # -----------------------------
    # Get Transactions (FIXED)
    # -----------------------------
    def get_transactions(self, customer_id: int):
        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT 
                    t.id,
                    t.transaction_type,
                    t.amount,
                    t.balance_after,
                    t.reference,
                    t.created_at,
                    a.account_number
                FROM transactions t
                JOIN accounts a ON t.account_id = a.id
                WHERE a.customer_id = %s
                ORDER BY t.created_at DESC
            """, (customer_id,))

            return cursor.fetchall()

        finally:
            conn.close()