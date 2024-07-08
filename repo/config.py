import mysql.connector
from flask import jsonify, request
import os
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

# Getting environment variables
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")
SECRET_KEY = os.getenv("SECRET_KEY")
ADMIN_ACCESS_TOKEN = os.getenv("ADMIN_ACCESS_TOKEN")

# Function to establish database connection
def get_database_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE
        )
        if connection.is_connected():
            print("Connected to MySQL database")
        return connection

    except mysql.connector.Error as error:
        print(f"Error connecting to MySQL: {error}")
        raise  # Re-raise the exception for handling elsewhere

def generate_token(user_id):
    expiration = datetime.utcnow() + timedelta(minutes=180)
    token = jwt.encode({'user_id': user_id, 'exp': expiration}, SECRET_KEY, algorithm='HS256')
    return token

def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']

        # Check if the user_id exists in the officer table
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT officer_id FROM officer WHERE officer_id = %s", (user_id,))
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        if result:
            return user_id
        else:
            return None
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def admin_role_required(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message": "Token is missing"}), 401

        token = token.split(' ')[1]  # Extract token from header

        if token != ADMIN_ACCESS_TOKEN:
            return jsonify({"message": "Unauthorized access"}), 403

        return func(*args, **kwargs)

    return wrapper
