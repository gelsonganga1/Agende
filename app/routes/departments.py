from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..extensions import db
from ..models import Department, Appointment

departments_bp = Blueprint("departments", __name__, url_prefix="/api/departments")


@departments_bp.route("", methods=["GET"])
def list_departments():
    """
    Listar todos os departamentos
    ---
    responses:
      200:
        description: Lista de departamentos
    """
    departments = Department.query.all()
    return jsonify([d.to_dict() for d in departments]), 200


@departments_bp.route("/<int:dept_id>", methods=["GET"])
def get_department(dept_id):
    """
    Obter um departamento pelo ID
    ---
    parameters:
      - name: dept_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Dados do departamento
      404:
        description: Departamento não encontrado
    """
    department = Department.query.get_or_404(dept_id)
    return jsonify(department.to_dict()), 200


@departments_bp.route("", methods=["POST"])
@jwt_required()
def create_department():
    """
    Criar um novo departamento
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
            name:
              type: string
              example: Serviço de Migração
            address:
              type: string
              example: Rua Principal, Luanda
            phone:
              type: string
              example: 222000000
    responses:
      201:
        description: Departamento criado
      400:
        description: Nome é obrigatório
    """
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


@departments_bp.route("/<int:dept_id>/appointments", methods=["GET"])
@jwt_required()
def department_appointments(dept_id):
    """
    Listar agendamentos de um departamento
    ---
    security:
      - Bearer: []
    parameters:
      - name: dept_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lista de agendamentos do departamento
    """
    department = Department.query.get_or_404(dept_id)
    appointments = Appointment.query.filter_by(department_id=dept_id).order_by(Appointment.date, Appointment.time).all()
    return jsonify([a.to_dict() for a in appointments]), 200


@departments_bp.route("/<int:dept_id>", methods=["PUT"])
@jwt_required()
def update_department(dept_id):
    """
    Actualizar um departamento
    ---
    security:
      - Bearer: []
    parameters:
      - name: dept_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            address:
              type: string
            phone:
              type: string
    responses:
      200:
        description: Departamento actualizado
      400:
        description: Dados inválidos
    """
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
    """
    Remover um departamento
    ---
    security:
      - Bearer: []
    parameters:
      - name: dept_id
        in: path
        type: integer
        required: true
    responses:
      204:
        description: Departamento removido
    """
    department = Department.query.get_or_404(dept_id)
    db.session.delete(department)
    db.session.commit()
    return "", 204
