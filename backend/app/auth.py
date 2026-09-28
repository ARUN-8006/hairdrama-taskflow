from functools import wraps
from flask import request, jsonify
import jwt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from .config import settings
from .db import supabase


def verify_google_id_token(token: str):
    if not settings.GOOGLE_CLIENT_ID:
        raise ValueError("GOOGLE_CLIENT_ID is not configured")
    info = id_token.verify_oauth2_token(token, google_requests.Request(), settings.GOOGLE_CLIENT_ID)
    if info.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
        raise ValueError("Invalid token issuer")
    return info


def issue_session(user):
    payload = {"sub": str(user["id"]), "email": user["email"]}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def current_user():
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    try:
        payload = jwt.decode(header[7:], settings.JWT_SECRET, algorithms=["HS256"])
        if not supabase:
            return None
        result = supabase.table("users").select("*").eq("id", payload["sub"]).single().execute()
        return result.data
    except Exception:
        return None


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user:
            return jsonify({"error": "Authentication required"}), 401
        return fn(user, *args, **kwargs)
    return wrapper
