import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

BASE_URL = f"https://graph.facebook.com/v20.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"


# ==========================================================
# 1) ENVIAR PLANTILLA DE WHATSAPP
# ==========================================================
def send_whatsapp_template(to_number: str, template_name: str, variables: list = []):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "es_AR"}
        }
    }

    # Si la plantilla tiene variables, agregamos los "components"
    if variables:
        payload["template"]["components"] = [
            {
                "type": "body",
                "parameters": [{"type": "text", "text": v} for v in variables]
            }
        ]

    print("\n--- ENVIANDO PLANTILLA ---")
    print(json.dumps(payload, indent=4))

    response = requests.post(BASE_URL, headers=headers, json=payload)

    print("STATUS:", response.status_code)
    print("RESPUESTA:", response.text)

    return response.json()


# ==========================================================
# 2) ENVIAR MENSAJE DE TEXTO LIBRE
# ==========================================================
def send_whatsapp_text(to_number: str, message: str):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message}
    }

    print("\n--- ENVIANDO TEXTO ---")
    print(json.dumps(payload, indent=4))

    response = requests.post(BASE_URL, headers=headers, json=payload)

    print("STATUS:", response.status_code)
    print("RESPUESTA:", response.text)

    return response.json()
