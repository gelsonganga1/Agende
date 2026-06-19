from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models import db, Department

departments_bp = Blueprint("departments", __name__, url_prefix="/api/departments")


@departments_bp.route("", methods=["GET"])
def list_departments():
    departments = Department.query.all()
    return jsonify([d.to_dict() for d in departments]), 200


@departments_bp.route("/<int:dept_id>", methods=["GET"])
def get_department(dept_id):
    department = Department.query.get_or_404(dept_id)
    return jsonify(department.to_dict()), 200


@departments_bp.route("", methods=["POST"])
@jwt_required()
def create_department():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Nome é obrigatório"}), 400

    department = Department(
        name=data["name"],
        address=data.get("address"),
        phone=data.get("phone"),
    )
    db.session.add(department)
    db.session.commit()
    return jsonify(department.to_dict()), 201


@departments_bp.route("/<int:dept_id>", methods=["PUT"])
@jwt_required()
def update_department(dept_id):
    department = Department.query.get_or_404(dept_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    if "name" in data:
        department.name = data["name"]
    if "address" in data:
        department.address = data["address"]
    if "phone" in data:
        department.phone = data["phone"]

    db.session.commit()
    return jsonify(department.to_dict()), 200


@departments_bp.route("/<int:dept_id>", methods=["DELETE"])
@jwt_required()
def delete_department(dept_id):
    department = Department.query.get_or_404(dept_id)
    db.session.delete(department)
    db.session.commit()
    return "", 204
