from database.connection import get_connection
from datetime import datetime


class AccountRepository:

    def create_account(self, customer_id: int, account_type: str):
        account_number = self.generate_account_number()

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO accounts (customer_id, account_number, account_type, balance, status)
                VALUES (%s, %s, %s, 0, 'active')
                """,
                (customer_id, account_number, account_type)
            )
            conn.commit()
        finally:
            conn.close()

        return account_number

    def get_by_account_number(self, account_number):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM accounts WHERE account_number = %s",
                (account_number,)
            )
            return cursor.fetchone()
        finally:
            conn.close()

    def get_accounts_by_customer(self, customer_id: int):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, account_number, account_type, balance, status, created_at
                FROM accounts
                WHERE customer_id = %s
                """,
                (customer_id,)
            )
            return cursor.fetchall()
        finally:
            conn.close()

    def update_balance(self, account_id, new_balance, conn=None):
        close_conn = False
        if conn is None:
            conn = get_connection()
            close_conn = True
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE accounts SET balance = %s WHERE id = %s",
                (new_balance, account_id)
            )
            if close_conn:
                conn.commit()
        finally:
            if close_conn:
                conn.close()

    def generate_account_number(self):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(id) as max_id FROM accounts")
            row = cursor.fetchone()
        finally:
            conn.close()

        next_id = (row["max_id"] or 0) + 1
        year = datetime.now().year
        return f"GBK-{year}-{next_id:06d}"

    def get_account_by_id(self, account_id: int):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM accounts WHERE id = %s",
                (account_id,)
            )
            return cursor.fetchone()
        finally:
            conn.close()
