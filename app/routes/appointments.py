from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import Appointment

appointments_bp = Blueprint("appointments", __name__, url_prefix="/api/appointments")


@appointments_bp.route("", methods=["GET"])
@jwt_required()
def list_appointments():
    """
    Listar todos os agendamentos
    ---
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de agendamentos
    """
    appointments = Appointment.query.all()
    return jsonify([a.to_dict() for a in appointments]), 200


@appointments_bp.route("/<int:appt_id>", methods=["GET"])
@jwt_required()
def get_appointment(appt_id):
    """
    Obter um agendamento pelo ID
    ---
    security:
      - Bearer: []
    parameters:
      - name: appt_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Dados do agendamento
      404:
        description: Agendamento não encontrado
    """
    appointment = Appointment.query.get_or_404(appt_id)
    return jsonify(appointment.to_dict()), 200


@appointments_bp.route("", methods=["POST"])
@jwt_required()
def create_appointment():
    """
    Criar um novo agendamento
    ---
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            service_id:
              type: integer
              example: 1
            department_id:
              type: integer
              example: 1
            date:
              type: string
              example: 2026-07-15
            time:
              type: string
              example: 09:30
            notes:
              type: string
    responses:
      201:
        description: Agendamento criado
      400:
        description: Dados inválidos
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    user_id = get_jwt_identity()

    required = ["service_id", "date", "time"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"{field} é obrigatório"}), 400

    existing = Appointment.query.filter_by(
        user_id=int(user_id),
        service_id=data["service_id"],
    ).filter(Appointment.status != "cancelled").first()
    if existing:
        return jsonify({"error": "Já tens um agendamento para este serviço"}), 409

    slot_taken = Appointment.query.filter_by(
        service_id=data["service_id"],
        date=data["date"],
        time=data["time"],
    ).filter(Appointment.status != "cancelled").first()
    if slot_taken:
        return jsonify({"error": "Este horário já está reservado"}), 409

    appointment = Appointment(
        user_id=int(user_id),
        service_id=data["service_id"],
        department_id=data.get("department_id"),
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
    """
    Actualizar um agendamento
    ---
    security:
      - Bearer: []
    parameters:
      - name: appt_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            date:
              type: string
            time:
              type: string
            status:
              type: string
            notes:
              type: string
    responses:
      200:
        description: Agendamento actualizado
      400:
        description: Dados inválidos
    """
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
    """
    Remover um agendamento
    ---
    security:
      - Bearer: []
    parameters:
      - name: appt_id
        in: path
        type: integer
        required: true
    responses:
      204:
        description: Agendamento removido
    """
    appointment = Appointment.query.get_or_404(appt_id)
    db.session.delete(appointment)
    db.session.commit()
    return "", 204
