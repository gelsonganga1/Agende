import os
import re
import threading
import logging
import requests
from flask import current_app

logger = logging.getLogger(__name__)

OMBALA_API_URL = "https://api.useombala.ao/v1/messages"


def _format_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("244"):
        return digits
    if digits.startswith("00244"):
        return "244" + digits[5:]
    return "244" + digits


def _send(to: str, message: str, api_key: str, sender: str) -> None:
    formatted_to = _format_phone(to)
    logger.info(f"Sending SMS to {formatted_to}")
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "message": message,
        "from": sender or "AGENDAMENTO",
        "to": formatted_to,
    }
    try:
        resp = requests.post(OMBALA_API_URL, json=payload, headers=headers, timeout=30)
        if not resp.ok:
            logger.error(
                f"Ombala API error: {resp.status_code} | body: {resp.text}"
            )
        else:
            logger.info(f"Ombala API success: {resp.status_code} | body: {resp.text}")
    except requests.RequestException as e:
        logger.error(f"Ombala SMS request failed: {e}")


def send_sms(to: str, message: str) -> dict:
    api_key = current_app.config.get("OMBALA_API_KEY") or os.getenv("OMBALA_API_KEY")
    sender = current_app.config.get("OMBALA_SENDER_NAME") or os.getenv("OMBALA_SENDER_NAME")

    if not api_key or api_key == "cole-o-seu-token-aqui":
        current_app.logger.warning("Ombala API key not configured. SMS not sent.")
        return {"error": "API key not configured"}

    threading.Thread(target=_send, args=(to, message, api_key, sender), daemon=True).start()
    return {"message": "SMS sent in background"}
