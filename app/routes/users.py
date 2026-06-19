from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models import db, User
import bcrypt

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.route("", methods=["GET"])
@jwt_required()
def list_users():
    """
    Listar todos os utilizadores
    ---
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de utilizadores
    """
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200


@users_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    """
    Obter um utilizador pelo ID
    ---
    security:
      - Bearer: []
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Dados do utilizador
      404:
        description: Utilizador não encontrado
    """
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


@users_bp.route("/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    """
    Actualizar dados de um utilizador
    ---
    security:
      - Bearer: []
    parameters:
      - name: user_id
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
            email:
              type: string
            phone:
              type: string
            role:
              type: string
            password:
              type: string
    responses:
      200:
        description: Utilizador actualizado
      400:
        description: Dados inválidos
    """
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    if "name" in data:
        user.name = data["name"]
    if "email" in data:
        user.email = data["email"]
    if "phone" in data:
        user.phone = data["phone"]
    if "role" in data:
        user.role = data["role"]
    if "password" in data and data["password"]:
        hashed = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt())
        user.password = hashed.decode("utf-8")

    db.session.commit()
    return jsonify(user.to_dict()), 200


@users_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    """
    Remover um utilizador
    ---
    security:
      - Bearer: []
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      204:
        description: Utilizador removido
    """
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return "", 204
