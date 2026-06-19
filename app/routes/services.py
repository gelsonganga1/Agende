from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models import db, Service

services_bp = Blueprint("services", __name__, url_prefix="/api/services")


@services_bp.route("", methods=["GET"])
def list_services():
    services = Service.query.all()
    return jsonify([s.to_dict() for s in services]), 200


@services_bp.route("/<int:service_id>", methods=["GET"])
def get_service(service_id):
    service = Service.query.get_or_404(service_id)
    return jsonify(service.to_dict()), 200


@services_bp.route("", methods=["POST"])
@jwt_required()
def create_service():
    data = request.get_json()
    if not data or not data.get("name") or not data.get("department_id"):
        return jsonify({"error": "Nome e department_id são obrigatórios"}), 400

    service = Service(
        name=data["name"],
        description=data.get("description"),
        duration=data.get("duration"),
        price=data.get("price"),
        department_id=data["department_id"],
    )
    db.session.add(service)
    db.session.commit()
    return jsonify(service.to_dict()), 201


@services_bp.route("/<int:service_id>", methods=["PUT"])
@jwt_required()
def update_service(service_id):
    service = Service.query.get_or_404(service_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    if "name" in data:
        service.name = data["name"]
    if "description" in data:
        service.description = data["description"]
    if "duration" in data:
        service.duration = data["duration"]
    if "price" in data:
        service.price = data["price"]
    if "department_id" in data:
        service.department_id = data["department_id"]

    db.session.commit()
    return jsonify(service.to_dict()), 200


@services_bp.route("/<int:service_id>", methods=["DELETE"])
@jwt_required()
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    return "", 204
