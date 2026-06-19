from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..extensions import db
from ..models import User
from ..utils.ombala import send_sms
import bcrypt

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Registo de novo utilizador
    Cria uma conta com role "client". Envia um código OTP por SMS.
    O utilizador fica inativo até verificar o telefone.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: João Silva
            phone:
              type: string
              example: 921939411
            password:
              type: string
              example: minha-senha
            email:
              type: string
              example: joao@email.com
    responses:
      201:
        description: Utilizador criado com sucesso
      400:
        description: Dados inválidos
      409:
        description: Telefone ou email já registado
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    name = data.get("name")
    phone = data.get("phone")
    password = data.get("password")
    email = data.get("email")

    if not name or not phone or not password:
        return jsonify({"error": "Nome, telefone e password são obrigatórios"}), 400

    if User.query.filter_by(phone=phone).first():
        return jsonify({"error": "Telefone já registado"}), 409

    if email and User.query.filter_by(email=email).first():
        return jsonify({"error": "Email já registado"}), 409

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    user = User(
        name=name,
        phone=phone,
        password=hashed.decode("utf-8"),
        email=email or None,
        role="client",
        is_active=False,
        is_phone_verified=False,
    )
    db.session.add(user)
    db.session.commit()

    code = user.generate_otp()
    db.session.commit()
    message = f"O seu código de verificação Agendamento Angola é: {code}. Válido por 5 minutos."
    send_sms(phone, message)

    resp = user.to_dict()
    resp["otp_code"] = code

    return jsonify(resp), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Autenticação do utilizador
    Retorna tokens JWT (access + refresh) se as credenciais forem válidas.
    Aceita email ou telefone como login.
    Se o telefone não estiver verificado, retorna 403 com requires_otp=true.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            login:
              type: string
              example: joao@email.com
            password:
              type: string
              example: minha-senha
    responses:
      200:
        description: Login bem-sucedido, retorna tokens
      401:
        description: Credenciais inválidas
      403:
        description: Telefone não verificado (requires_otp)
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    login = data.get("login") or data.get("email") or data.get("phone")
    password = data.get("password")

    if not login or not password:
        return jsonify({"error": "Login e password são obrigatórios"}), 400

    user = User.query.filter(
        (User.email == login) | (User.phone == login)
    ).first()
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
    """
    Perfil do utilizador autenticado
    ---
    security:
      - Bearer: []
    responses:
      200:
        description: Dados do utilizador
      404:
        description: Utilizador não encontrado
    """
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"error": "Utilizador não encontrado"}), 404
    return jsonify(user.to_dict()), 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required()
def refresh():
    """
    Renovar token de acesso
    ---
    security:
      - Bearer: []
    responses:
      200:
        description: Novo access token
    """
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=str(user_id))
    return jsonify({"access": access_token}), 200
