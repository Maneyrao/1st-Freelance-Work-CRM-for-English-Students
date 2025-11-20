import os
from dotenv import load_dotenv
import requests #solicitud a la api de meta

#lee las variables desde .env
load_dotenv()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

#el número tiene que tener formato internacional si o sí, sin el +, 5491122235497 por ejemplo (arg)
def send_whatsapp_message(to_number: str, message: str):
    url = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}", #si no tuviera el token devuelve 401
        "Content-Type": "application/json"
    }
    
    #Intepreta el mensaje que "enviamos" en python pero lo adapta al formato de html de meta.
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number, 
                        
        "type": "text",
        "text": {"body": message} 
    }

    response = requests.post(url, headers=headers, json=payload)
    print(response.status_code, response.text)
    return response.json()
