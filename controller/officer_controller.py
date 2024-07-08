from flask import jsonify, Blueprint, request
from service.officer_service import Officer
from flask_cors import CORS
from repo.config import admin_role_required
import re

# Create a Blueprint for the officer controller
officer_controller = Blueprint('officer_controller', __name__)
CORS(officer_controller)

class OfficerController:

    __officer_service = Officer()

    @staticmethod
    @officer_controller.route('/', methods=["GET"])
    def get_all_officers():
        try:
            # Add logic to fetch all officers
            officers = OfficerController.__officer_service.get_all_officers()
            return jsonify({"message": "Officers retrieved successfully", "data": officers}), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 500

    @staticmethod
    @officer_controller.route('/<int:officer_id>', methods=["GET"])
    def get_officer(officer_id):
        try:
            result = OfficerController.__officer_service.get_officer(officer_id)
            if result['data']:
                return jsonify(result), 200
            else:
                return jsonify(result), 404
        except Exception as e:
            return jsonify({"message": str(e)}), 500

    @staticmethod
    @officer_controller.route('/register', methods=["POST"])
    def register_officer():
        data = request.json
        
        # Validation
        if 'officer_name' not in data or not data['officer_name'].strip():
            return jsonify({"message": "Officer name is required"}), 400
        if 'officer_nic' not in data or not data['officer_nic'].strip():
            return jsonify({"message": "Valid NIC is required"}), 400
        if 'officer_username' not in data or not data['officer_username'].strip():
            return jsonify({"message": "Username is required"}), 400
        if 'officer_email' not in data or not re.match(r'^\S+@\S+\.\S+$', data['officer_email']):
            return jsonify({"message": "Valid email is required"}), 400
        if 'officer_password' not in data or len(data['officer_password']) < 8:
            return jsonify({"message": "Password must be at least 8 characters long"}), 400

        result = OfficerController.__officer_service.save_officer(data)
        if result['message'] == "Officer saved successfully":
            return jsonify(result), 201
        else:
            return jsonify(result), 500

    @staticmethod
    @officer_controller.route('/login', methods=["POST"])
    def login():
        data = request.json

        # Validation
        if 'officer_password' not in data or not data['officer_password'].strip():
            return jsonify({"message": "Password is required"}), 400
        if not any([data.get('officer_username'), data.get('officer_email'), data.get('officer_phone_number')]):
            return jsonify({"message": "Username, email, or phone number is required"}), 400

        result = OfficerController.__officer_service.login(data)
        if result['message'] == "Login successful":
            return jsonify(result), 200
        else:
            return jsonify(result), 401


    @staticmethod
    @officer_controller.route('/<string:officer_token>', methods=["PUT"])
    def update_officer(officer_token):
        data = request.json
        
        # Validation (similar to registration but allows partial updates)
        if 'officer_email' in data and not re.match(r'^\S+@\S+\.\S+$', data['officer_email']):
            return jsonify({"message": "Valid email is required"}), 400
        if 'officer_password' in data and len(data['officer_password']) < 8:
            return jsonify({"message": "Password must be at least 8 characters long"}), 400
        
        result = OfficerController.__officer_service.update_officer(officer_token, data)
        
        if result['message'] == "Officer updated successfully":
            return jsonify(result), 200
        else:
            return jsonify(result), 500

    @staticmethod
    @officer_controller.route('/<int:officer_id>', methods=["DELETE"]) #office use only | allowed to user setting champion
    @admin_role_required
    def delete_officer(officer_id):
        try:
            result = OfficerController.__officer_service.delete_officer(officer_id)
            if result['message'] == "Officer deleted successfully":
                return jsonify(result), 200
            else:
                return jsonify(result), 500
        except Exception as e:
            return jsonify({"message": str(e)}), 500
