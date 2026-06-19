from flask import Blueprint, jsonify
from .auth import auth_bp
from .users import users_bp
from .departments import departments_bp
from .services import services_bp
from .appointments import appointments_bp
from .otp import otp_bp

api = Blueprint("api", __name__)


@api.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


api.register_blueprint(auth_bp)
api.register_blueprint(users_bp)
api.register_blueprint(departments_bp)
api.register_blueprint(services_bp)
api.register_blueprint(appointments_bp)
api.register_blueprint(otp_bp)
