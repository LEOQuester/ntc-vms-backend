from datetime import datetime
from repo.config import get_database_connection, decode_token, generate_token
import mysql.connector

class Vehicle:
    def __init__(self):
        self.connection = get_database_connection()

    def save_vehicle(self, officer_token, data):
        officer_id = decode_token(officer_token)

        if officer_id is None:
            return {"message": "Token invalid or expired"}

        try:
            officer_id = int(officer_id)
        except ValueError:
            return {"message": "Invalid officer ID in token"}
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Current timestamp for vehicle added date and time
            vehicle_added_dateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # SQL INSERT statement
            insert_query = """
                INSERT INTO vehicle (
                    vehicle_number, product_year, initial_meter_reading, vehicle_type,
                    service_km_range, engine_number, chassy_number, vehicle_status,
                    liscense_expire_date, insurance_expire_date, special_notes,
                    vehicle_added_dateTime, vehicle_added_officer
                ) VALUES (
                    %(vehicle_number)s, %(product_year)s, %(initial_meter_reading)s, %(vehicle_type)s,
                    %(service_km_range)s, %(engine_number)s, %(chassy_number)s, %(vehicle_status)s,
                    %(liscense_expire_date)s, %(insurance_expire_date)s, %(special_notes)s,
                    %(vehicle_added_dateTime)s, %(vehicle_added_officer)s
                )
            """
            # Data to be inserted
            vehicle_data = {
                'vehicle_number': data['vehicle_number'],
                'product_year': data['product_year'],
                'initial_meter_reading': data['initial_meter_reading'],
                'vehicle_type': data['vehicle_type'],
                'service_km_range': data['service_km_range'],
                'engine_number': data['engine_number'],
                'chassy_number': data['chassy_number'],
                'vehicle_status': data['vehicle_status'],
                'liscense_expire_date': data.get('liscense_expire_date'),
                'insurance_expire_date': data.get('insurance_expire_date'),
                'special_notes': data.get('special_notes'),
                'vehicle_added_dateTime': vehicle_added_dateTime,
                'vehicle_added_officer': officer_id
            }

            cursor.execute(insert_query, vehicle_data)
            self.connection.commit()
            cursor.close()

            return {
                "message": "Vehicle saved successfully",
                "data": data
            }

        except mysql.connector.Error as error:
            return {
                "message": f"Error saving vehicle: {error}",
                "data": data
            }

    def update_vehicle(self, officer_token, vehicle_id, data):
        officer_id = decode_token(officer_token)

        if officer_id is None:
            return {"message": "Token invalid or expired"}

        try:
            officer_id = int(officer_id)
        except ValueError:
            return {"message": "Invalid officer ID in token"}
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)

            # SQL UPDATE statement
            update_query = "UPDATE vehicle SET " + ", ".join(f"{key} = %({key})s" for key in data.keys()) + " WHERE vehicle_id = %(vehicle_id)s"
            data['vehicle_id'] = vehicle_id

            cursor.execute(update_query, data)
            self.connection.commit()
            cursor.close()

            return {
                "message": "Vehicle updated successfully",
                "data": data
            }

        except mysql.connector.Error as error:
            return {
                "message": f"Error updating vehicle: {error}",
                "data": data
            }

        finally:
            if cursor:
                cursor.close()

    def delete_vehicle(self, officer_token, vehicle_id):
        officer_id = int(decode_token(officer_token))
        if not officer_id:
            return {
                "message": "Token invalid or expired",
            }
        try:
            cursor = self.connection.cursor()

            # SQL DELETE statement
            delete_query = "DELETE FROM vehicle WHERE vehicle_id = %s"
            cursor.execute(delete_query, (vehicle_id,))
            self.connection.commit()
            cursor.close()

            return {
                "message": "Vehicle deleted successfully",
                "data": None
            }

        except mysql.connector.Error as error:
            return {
                "message": f"Error deleting vehicle: {error}",
                "data": None
            }

    def get_vehicle(self, vehicle_id):
        try:
            cursor = self.connection.cursor(dictionary=True)
            # SQL SELECT statement
            select_query = "SELECT * FROM vehicle WHERE vehicle_id = %s"
            cursor.execute(select_query, (vehicle_id,))
            vehicle = cursor.fetchone()
            cursor.close()

            if vehicle:
                return {
                    "message": "Vehicle retrieved successfully",
                    "data": vehicle
                }
            else:
                return {
                    "message": "Vehicle not found",
                    "data": None
                }

        except mysql.connector.Error as error:
            return {
                "message": f"Error retrieving vehicle: {error}",
                "data": None
            }

    def get_all_vehicles(self):
        try:
            cursor = self.connection.cursor(dictionary=True)
            # SQL SELECT statement to get all vehicles
            select_query = "SELECT * FROM vehicle"
            cursor.execute(select_query)
            vehicles = cursor.fetchall()
            cursor.close()

            return {
                "message": "Vehicles retrieved successfully",
                "data": vehicles
            }

        except mysql.connector.Error as error:
            return {
                "message": f"Error retrieving vehicles: {error}",
                "data": None
            }

    def __del__(self):
        # Closing the connection
        if getattr(self, 'connection', None) and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection is closed")
