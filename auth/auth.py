import logging
import jwt
import requests
from config import JWT_SECRET, BACKEND_URL
from db.methods import get_dialog
from db.db_module import connect_to_db


def get_api_key(chat_id, name=None, image_url=None):
    connect_to_db()
    try:
        api_key = get_dialog(chat_id).api_key
        return 200, {"api_key": api_key}
    except:
        payload = {
            "id": chat_id,
            "name": name,
            "image": image_url
        }

        try:
            token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        except Exception as e:
            logging.error("Failed to encode user auth data with JWT", e)
            return 403, {"error": "Failed to encode user auth data with JWT", "message": str(e)}

        post_payload = {
            "token": token
        }

        try:
            response = requests.post(f"{BACKEND_URL}/auth", json=post_payload)
            return response.status_code, response.json()
        except Exception as e:
            logging.error("Auth post request failed")
            return 500, {"error": "Internal Server Error", "message": str(e)}