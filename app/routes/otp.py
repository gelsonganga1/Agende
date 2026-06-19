from flask import Blueprint, request, jsonify
from ..models import db, User
from ..utils.ombala import send_sms

otp_bp = Blueprint("otp", __name__, url_prefix="/api/users")


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
            email:
              type: string
              example: joao@email.com
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
            email:
              type: string
              example: joao@email.com
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
            email:
              type: string
              example: joao@email.com
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
