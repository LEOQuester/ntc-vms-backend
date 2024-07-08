from flask import Flask
from flask_cors import CORS
from repo.prefix_middleware import PrefixMiddleware

#my imports
from controller.officer_controller import officer_controller
from controller.vehicle_controller import vehicle_controller

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

app.register_blueprint(officer_controller, url_prefix="/officers")
app.register_blueprint(vehicle_controller, url_prefix="/vehicles")


app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/api')


if __name__ == '__main__':
    app.run(debug=True)
