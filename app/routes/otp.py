import re
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import User
from ..utils.ombala import send_sms


def _valid_angolan_phone(phone: str) -> bool:
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("244"):
        digits = digits[3:]
    elif digits.startswith("00244"):
        digits = digits[5:]
    return len(digits) == 9 and digits.startswith("9")

otp_bp = Blueprint("otp", __name__, url_prefix="/api/auth")


@otp_bp.route("/send-otp", methods=["POST"])
def send_otp():
    """
    Enviar código OTP por SMS
    Gera um código de 6 dígitos e envia para o telefone do utilizador via Ombala.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            phone:
              type: string
              example: 921939411
    responses:
      200:
        description: Código enviado (pode conter warning se SMS não foi entregue)
      400:
        description: Dados inválidos
      404:
        description: Utilizador não encontrado
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    phone = data.get("phone")
    if not phone:
        return jsonify({"error": "Telefone é obrigatório"}), 400

    if not _valid_angolan_phone(phone):
        return jsonify({"error": "Número de telefone angolano inválido (ex: 921939411)"}), 400

    user = User.query.filter_by(phone=phone).first()
    if not user:
        return jsonify({"error": "Utilizador não encontrado"}), 404

    code = user.generate_otp()
    db.session.commit()

    message = f"O seu código de verificação Agendamento Angola é: {code}. Válido por 5 minutos."
    send_sms(user.phone, message)

    return jsonify({"message": "Código enviado com sucesso", "otp_code": code}), 200


@otp_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    """
    Verificar código OTP
    Valida o código de 6 dígitos e activa a conta do utilizador.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            phone:
              type: string
              example: 921939411
            code:
              type: string
              example: 483920
    responses:
      200:
        description: Telefone verificado com sucesso
      400:
        description: Código inválido ou expirado
      404:
        description: Utilizador não encontrado
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    phone = data.get("phone")
    code = data.get("code")

    if not phone or not code:
        return jsonify({"error": "Telefone e código são obrigatórios"}), 400

    user = User.query.filter_by(phone=phone).first()
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
    """
    Reenviar código OTP
    Gera um novo código e envia novamente por SMS.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            phone:
              type: string
              example: 921939411
    responses:
      200:
        description: Código reenviado
      400:
        description: Dados inválidos
      404:
        description: Utilizador não encontrado
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    phone = data.get("phone")
    if not phone:
        return jsonify({"error": "Telefone é obrigatório"}), 400

    if not _valid_angolan_phone(phone):
        return jsonify({"error": "Número de telefone angolano inválido (ex: 921939411)"}), 400

    user = User.query.filter_by(phone=phone).first()
    if not user:
        return jsonify({"error": "Utilizador não encontrado"}), 404

    code = user.generate_otp()
    db.session.commit()

    message = f"O seu código de verificação Agendamento Angola é: {code}. Válido por 5 minutos."
    send_sms(user.phone, message)

    return jsonify({"message": "Código reenviado com sucesso", "otp_code": code}), 200
