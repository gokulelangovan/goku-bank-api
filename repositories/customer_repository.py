from database.connection import get_connection


class CustomerRepository:

    def create_customer(self, full_name, email, phone):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO customers (full_name, email, phone)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (full_name, email, phone)
            )
            customer_id = cursor.fetchone()["id"]
            conn.commit()
            return customer_id
        finally:
            conn.close()

    def get_by_email(self, email):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM customers WHERE email = %s",
                (email,)
            )
            return cursor.fetchone()
        finally:
            conn.close()

    def get_customer_by_id(self, customer_id: int):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, full_name, email, phone, created_at FROM customers WHERE id = %s",
                (customer_id,)
            )
            return cursor.fetchone()
        finally:
            conn.close()
