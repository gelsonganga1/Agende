from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..models import db, User, Department
from ..utils.ombala import send_sms
import bcrypt

auth_bp = Blueprint("auth", __name__, url_prefix="/api/users")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    phone = data.get("phone")

    if not name or not email or not password:
        return jsonify({"error": "Nome, email e password são obrigatórios"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email já registado"}), 409

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    user = User(
        name=name,
        email=email,
        password=hashed.decode("utf-8"),
        phone=phone,
        role="client",
        is_active=False,
        is_phone_verified=False,
    )
    db.session.add(user)
    db.session.commit()

    if phone:
        code = user.generate_otp()
        db.session.commit()
        message = f"O seu código de verificação Agendamento Angola é: {code}. Válido por 5 minutos."
        send_sms(phone, message)

    return jsonify(user.to_dict()), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email e password são obrigatórios"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Credenciais inválidas"}), 401

    if not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        return jsonify({"error": "Credenciais inválidas"}), 401

    if not user.is_phone_verified:
        return jsonify({
            "error": "Telefone não verificado",
            "requires_otp": True,
            "email": user.email,
            "phone": user.phone,
        }), 403

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_access_token(identity=str(user.id))

    return jsonify({
        "user": user.to_dict(),
        "access": access_token,
        "refresh": refresh_token,
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"error": "Utilizador não encontrado"}), 404
    return jsonify(user.to_dict()), 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required()
def refresh():
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=str(user_id))
    return jsonify({"access": access_token}), 200
