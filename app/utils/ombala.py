import os
import re
import threading
import requests
from flask import current_app

OMBALA_API_URL = "https://api.useombala.ao/v1/messages"


def _format_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("+244"):
        return digits[4:]
    if digits.startswith("00244"):
        return digits[5:]
    if digits.startswith("244"):
        return digits[3:]
    return digits


def _send(to: str, message: str, api_key: str, sender: str) -> None:
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "message": message,
        "from": sender or "AGENDAMENTO",
        "to": _format_phone(to),
    }
    try:
        resp = requests.post(OMBALA_API_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        detail = ""
        if hasattr(e, "response") and e.response is not None:
            detail = e.response.text
        import logging
        logging.getLogger(__name__).error(f"Ombala SMS error: {e} | detail: {detail}")


def send_sms(to: str, message: str) -> dict:
    api_key = current_app.config.get("OMBALA_API_KEY") or os.getenv("OMBALA_API_KEY")
    sender = current_app.config.get("OMBALA_SENDER_NAME") or os.getenv("OMBALA_SENDER_NAME")

    if not api_key or api_key == "cole-o-seu-token-aqui":
        current_app.logger.warning("Ombala API key not configured. SMS not sent.")
        return {"error": "API key not configured"}

    threading.Thread(target=_send, args=(to, message, api_key, sender), daemon=True).start()
    return {"message": "SMS sent in background"}
