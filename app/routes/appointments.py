from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Appointment

appointments_bp = Blueprint("appointments", __name__, url_prefix="/api/appointments")


@appointments_bp.route("", methods=["GET"])
@jwt_required()
def list_appointments():
    appointments = Appointment.query.all()
    return jsonify([a.to_dict() for a in appointments]), 200


@appointments_bp.route("/<int:appt_id>", methods=["GET"])
@jwt_required()
def get_appointment(appt_id):
    appointment = Appointment.query.get_or_404(appt_id)
    return jsonify(appointment.to_dict()), 200


@appointments_bp.route("", methods=["POST"])
@jwt_required()
def create_appointment():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    user_id = get_jwt_identity()

    required = ["service_id", "department_id", "date", "time"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"{field} é obrigatório"}), 400

    appointment = Appointment(
        user_id=int(user_id),
        service_id=data["service_id"],
        department_id=data["department_id"],
        date=data["date"],
        time=data["time"],
        notes=data.get("notes"),
    )
    db.session.add(appointment)
    db.session.commit()
    return jsonify(appointment.to_dict()), 201


@appointments_bp.route("/<int:appt_id>", methods=["PUT"])
@jwt_required()
def update_appointment(appt_id):
    appointment = Appointment.query.get_or_404(appt_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    if "date" in data:
        appointment.date = data["date"]
    if "time" in data:
        appointment.time = data["time"]
    if "status" in data:
        appointment.status = data["status"]
    if "notes" in data:
        appointment.notes = data["notes"]

    db.session.commit()
    return jsonify(appointment.to_dict()), 200


@appointments_bp.route("/<int:appt_id>", methods=["DELETE"])
@jwt_required()
def delete_appointment(appt_id):
    appointment = Appointment.query.get_or_404(appt_id)
    db.session.delete(appointment)
    db.session.commit()
    return "", 204
