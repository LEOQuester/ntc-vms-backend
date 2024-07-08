from flask import jsonify, Blueprint, request
from service.vehicle_service import Vehicle
from flask_cors import CORS
import re

# Create a Blueprint for the vehicle controller
vehicle_controller = Blueprint('vehicle_controller', __name__)
CORS(vehicle_controller)

class VehicleController:

    __vehicle_service = Vehicle()

    @staticmethod
    @vehicle_controller.route('/', methods=["GET"])
    def get_all_vehicles():
        try:
            vehicles = VehicleController.__vehicle_service.get_all_vehicles()
            return jsonify({"message": "Vehicles retrieved successfully", "data": vehicles}), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 500

    @staticmethod
    @vehicle_controller.route('/<int:vehicle_id>', methods=["GET"])
    def get_vehicle(vehicle_id):
        try:
            result = VehicleController.__vehicle_service.get_vehicle(vehicle_id)
            if result['data']:
                return jsonify(result), 200
            else:
                return jsonify(result), 404
        except Exception as e:
            return jsonify({"message": str(e)}), 500

    @staticmethod
    @vehicle_controller.route('/register/', methods=["POST"])
    def register_vehicle():
        officer_token = request.headers.get('Authorization')
        if officer_token is None:
             return jsonify({"message": "Unautharized access!"}), 400
        
        print(officer_token)
        data = request.json

        # Validation
        if 'vehicle_number' not in data or not data['vehicle_number'].strip():
            return jsonify({"message": "Vehicle number is required"}), 400
        if 'product_year' not in data or not isinstance(data['product_year'], int):
            return jsonify({"message": "Valid product year is required"}), 400
        if 'initial_meter_reading' not in data or not isinstance(data['initial_meter_reading'], int):
            return jsonify({"message": "Initial meter reading is required"}), 400
        if 'vehicle_type' not in data or not data['vehicle_type'].strip():
            return jsonify({"message": "Vehicle type is required"}), 400

        result = VehicleController.__vehicle_service.save_vehicle(officer_token, data)
        if result['message'] == "Vehicle saved successfully":
            return jsonify(result), 201
        else:
            return jsonify(result), 500

    @staticmethod
    @vehicle_controller.route('/<int:vehicle_id>', methods=["PUT"])
    def update_vehicle(vehicle_id):
        officer_token = request.headers.get('Authorization')
        data = request.json
        print("data passed")
        # Validation
        if 'vehicle_number' in data and not data['vehicle_number'].strip():
            return jsonify({"message": "Vehicle number is required"}), 400
        if 'product_year' in data and not isinstance(data['product_year'], int):
            return jsonify({"message": "Valid product year is required"}), 400
        if 'initial_meter_reading' in data and not isinstance(data['initial_meter_reading'], int):
            return jsonify({"message": "Initial meter reading is required"}), 400
        if 'vehicle_type' in data and not data['vehicle_type'].strip():
            return jsonify({"message": "Vehicle type is required"}), 400
        print("validations passed")
        result = VehicleController.__vehicle_service.update_vehicle(officer_token, vehicle_id, data)
        if result['message'] == "Vehicle updated successfully":
            return jsonify(result), 200
        else:
            return jsonify(result), 500

    @staticmethod
    @vehicle_controller.route('/<int:vehicle_id>', methods=["DELETE"])
    def delete_vehicle( vehicle_id):
        officer_token = request.headers.get('Authorization')
        try:
            result = VehicleController.__vehicle_service.delete_vehicle(officer_token, vehicle_id)
            if result['message'] == "Vehicle deleted successfully":
                return jsonify(result), 200
            else:
                return jsonify(result), 500
        except Exception as e:
            return jsonify({"message": str(e)}), 500

