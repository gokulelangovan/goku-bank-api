from datetime import datetime
from database.connection import get_connection


class TransactionRepository:

    def create_transaction(self, account_id, transaction_type, amount, reference=None, conn=None):
        local_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        close_conn = False
        if conn is None:
            conn = get_connection()
            close_conn = True

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO transactions
                (account_id, transaction_type, amount, reference, created_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (account_id, transaction_type, amount, reference, local_time)
            )
            transaction_id = cursor.fetchone()["id"]

            if close_conn:
                conn.commit()

            return transaction_id
        finally:
            if close_conn:
                conn.close()

    def get_transactions_by_account(self, account_id: int):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT transaction_type, amount, reference, created_at
                FROM transactions
                WHERE account_id = %s
                ORDER BY created_at DESC
                """,
                (account_id,)
            )
            return cursor.fetchall()
        finally:
            conn.close()
