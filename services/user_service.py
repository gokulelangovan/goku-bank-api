from database.connection import get_connection


def get_customer_id_by_user(user_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT customer_id FROM users WHERE id = %s",
            (user_id,)
        )
        row = cursor.fetchone()

        if row is None:
            raise Exception("User not found")

        return row["customer_id"]
    finally:
        conn.close()
