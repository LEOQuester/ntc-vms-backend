import bcrypt
from datetime import datetime
from repo.config import get_database_connection, generate_token, decode_token
import mysql.connector


class Officer:
    def __init__(self):
        self.connection = get_database_connection()

    def save_officer(self, data):
        try:
            cursor = self.connection.cursor(dictionary=True)

            # Check for existing username, email, or phone number
            check_query = """
                SELECT officer_id FROM officer
                WHERE officer_username = %(officer_username)s
                OR officer_email = %(officer_email)s
                OR officer_phone_number = %(officer_phone_number)s
            """
            cursor.execute(check_query, {
                'officer_username': data['officer_username'],
                'officer_email': data['officer_email'],
                'officer_phone_number': data.get('officer_phone_number')
            })
            existing_officer = cursor.fetchone()

            if existing_officer:
                cursor.close()
                return {
                    "message": "Username, email, or phone number already exists",
                    "data": data
                }

            # Hash the password
            password_hash = bcrypt.hashpw(data['officer_password'].encode('utf-8'), bcrypt.gensalt())

            # Current timestamp for registration date and time
            reg_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # SQL INSERT statement
            insert_query = """
                INSERT INTO officer (
                    officer_name, officer_grade, officer_nic, officer_reg_dateTime,
                    officer_username, officer_email, officer_password_hash,
                    officer_phone_number, officer_position, officer_role,
                    officer_power_level, committee, status
                ) VALUES (
                    %(officer_name)s, %(officer_grade)s, %(officer_nic)s, %(officer_reg_dateTime)s,
                    %(officer_username)s, %(officer_email)s, %(officer_password_hash)s,
                    %(officer_phone_number)s, %(officer_position)s, %(officer_role)s,
                    %(officer_power_level)s, %(committee)s, %(status)s
                )
            """
            # Data to be inserted
            officer_data = {
                'officer_name': data['officer_name'],
                'officer_grade': data.get('officer_grade', None),
                'officer_nic': data['officer_nic'],
                'officer_reg_dateTime': reg_date_time,
                'officer_username': data['officer_username'],
                'officer_email': data['officer_email'],
                'officer_password_hash': password_hash,  # Use the hashed password
                'officer_phone_number': data.get('officer_phone_number', None),
                'officer_position': data.get('officer_position', None),
                'officer_role': data.get('officer_role', None),
                'officer_power_level': data.get('officer_power_level', None),
                'committee': data.get('committee', None),
                'status': 'active'
            }

            cursor.execute(insert_query, officer_data)
            self.connection.commit()
            cursor.close()

            return {
                "message": "Officer saved successfully",
                "data": data
            }

        except mysql.connector.Error as error:
            return {
                "message": f"Error saving officer: {error}",
                "data": data
            }
        


    def login(self, data):
        try:
            cursor = self.connection.cursor(dictionary=True)

            # Construct the WHERE clause based on available login credentials
            if 'officer_username' in data:
                where_clause = "officer_username = %s"
                value = data['officer_username']
            elif 'officer_email' in data:
                where_clause = "officer_email = %s"
                value = data['officer_email']
            elif 'officer_phone_number' in data:
                where_clause = "officer_phone_number = %s"
                value = data['officer_phone_number']

            # SQL SELECT statement to get the officer's hashed password
            select_query = f"SELECT officer_id, officer_password_hash FROM officer WHERE {where_clause}"
            cursor.execute(select_query, (value,))
            officer = cursor.fetchone()
            cursor.close()

            if officer and bcrypt.checkpw(data['officer_password'].encode('utf-8'), officer['officer_password_hash'].encode('utf-8')):
                token = generate_token(user_id=officer['officer_id'])
                return {
                    "message": "Login successful",
                    "data": {
                        "token": f"{token}"
                    }
                }
            else:
                return {
                    "message": "Invalid username, email, phone number or password",
                    "data": None
                }

        except mysql.connector.Error as error:
            return {
                "message": f"Error during login: {error}",
                "data": None
            }

    def get_officer(self, officer_id):
        try:
            cursor = self.connection.cursor(dictionary=True)
            # SQL SELECT statement
            select_query = "SELECT * FROM officer WHERE officer_id = %s"
            cursor.execute(select_query, (officer_id,))
            officer = cursor.fetchone()
            cursor.close()

            if officer:
                return {
                    "message": "Officer retrieved successfully",
                    "data": officer
                }
            else:
                return {
                    "message": "Officer not found",
                    "data": None
                }

        except mysql.connector.Error as error:
            return {
                "message": f"Error retrieving officer: {error}",
                "data": None
            }

    def update_officer(self, officer_token, data):
        officer_id = decode_token(officer_token)

        if officer_id is None:
            return {"message": "Token invalid or expired"}

        try:
            officer_id = int(officer_id)
        except ValueError:
            return {"message": "Invalid officer ID in token"}

        if not officer_id:
            return {
                "message": f"token invalid or expired",
            }
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)

            # Check for existing username, email, or phone number if being updated
            if 'officer_username' in data or 'officer_email' in data or 'officer_phone_number' in data:
                check_query = """
                    SELECT officer_id FROM officer
                    WHERE (officer_username = %(officer_username)s
                    OR officer_email = %(officer_email)s
                    OR officer_phone_number = %(officer_phone_number)s)
                    AND officer_id != %(officer_id)s
                """
                cursor.execute(check_query, {
                    'officer_username': data.get('officer_username', None),
                    'officer_email': data.get('officer_email', None),
                    'officer_phone_number': data.get('officer_phone_number', None),
                    'officer_id': officer_id
                })
                existing_officer = cursor.fetchone()

                if existing_officer:
                    return {
                        "message": "Username, email, or phone number already exists",
                        "data": {k: v for k, v in data.items() if k != 'officer_password'}
                    }

            # Hash the password if it is being updated
            if 'officer_password' in data:
                data['officer_password_hash'] = bcrypt.hashpw(data['officer_password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                del data['officer_password']

            # SQL UPDATE statement
            update_query = "UPDATE officer SET " + ", ".join(f"{key} = %({key})s" for key in data.keys()) + " WHERE officer_id = %(officer_id)s"
            data['officer_id'] = officer_id
            cursor.execute(update_query, data)
            self.connection.commit()

            del data['officer_id']
            return {
                "message": "Officer updated successfully",
                "data": {k: v for k, v in data.items() if k != 'officer_password_hash'}  # Ensure password hash is not included in response
            }

        except mysql.connector.Error as error:
            del data['officer_password']
            del data['officer_id']
            return {
                "message": f"Error updating officer: {error}",
                "data": {k: v for k, v in data.items() if k != 'officer_password_hash'}  # Ensure password hash is not included in error response
            }

        finally:
            if cursor:
                cursor.close()


    def delete_officer(self, officer_id):
        try:
            cursor = self.connection.cursor()

            # SQL DELETE statement
            delete_query = "DELETE FROM officer WHERE officer_id = %s"
            cursor.execute(delete_query, (officer_id,))
            self.connection.commit()
            cursor.close()

            return {
                "message": "Officer deleted successfully",
                "data": None
            }

        except mysql.connector.Error as error:
            return {
                "message": f"Officer not allowed to delete, related entries detected, {error}",
                "data": None
            }

    def __del__(self):
        # Closing the connection
        if getattr(self, 'connection', None) and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection is closed")
