from flask import Blueprint, request, jsonify
from ..models import db, User
from ..utils.ombala import send_sms
from flask_jwt_extended import jwt_required, get_jwt_identity

otp_bp = Blueprint("otp", __name__, url_prefix="/api/users")


@otp_bp.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    email = data.get("email")
    if not email:
        return jsonify({"error": "Email é obrigatório"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Utilizador não encontrado"}), 404

    if not user.phone:
        return jsonify({"error": "Utilizador não tem telefone registado"}), 400

    code = user.generate_otp()
    db.session.commit()

    message = f"O seu código de verificação Agendamento Angola é: {code}. Válido por 5 minutos."
    result = send_sms(user.phone, message)

    if "error" in result:
        return jsonify({"warning": "Não foi possível enviar SMS. Verifique as credenciais Ombala.", "code": code}), 200

    return jsonify({"message": "Código enviado com sucesso"}), 200


@otp_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    email = data.get("email")
    code = data.get("code")

    if not email or not code:
        return jsonify({"error": "Email e código são obrigatórios"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Utilizador não encontrado"}), 404

    if not user.verify_otp(code):
        return jsonify({"error": "Código inválido ou expirado"}), 400

    user.is_phone_verified = True
    user.is_active = True
    user.clear_otp()
    db.session.commit()

    return jsonify({"message": "Telefone verificado com sucesso"}), 200


@otp_bp.route("/resend-otp", methods=["POST"])
def resend_otp():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    email = data.get("email")
    if not email:
        return jsonify({"error": "Email é obrigatório"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Utilizador não encontrado"}), 404

    if not user.phone:
        return jsonify({"error": "Utilizador não tem telefone registado"}), 400

    code = user.generate_otp()
    db.session.commit()

    message = f"O seu código de verificação Agendamento Angola é: {code}. Válido por 5 minutos."
    result = send_sms(user.phone, message)

    if "error" in result:
        return jsonify({"warning": "Não foi possível enviar SMS. Verifique as credenciais Ombala.", "code": code}), 200

    return jsonify({"message": "Código reenviado com sucesso"}), 200
