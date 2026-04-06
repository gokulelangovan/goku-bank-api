from database.connection import get_connection


class UserRepository:

    def create_user(self, email, hashed_password):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (email, hashed_password)
                VALUES (%s, %s)
                RETURNING id
                """,
                (email, hashed_password)
            )
            user_id = cursor.fetchone()["id"]
            conn.commit()
            return user_id
        finally:
            conn.close()

    def get_user_by_email(self, email):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE email = %s",
                (email,)
            )
            return cursor.fetchone()
        finally:
            conn.close()
