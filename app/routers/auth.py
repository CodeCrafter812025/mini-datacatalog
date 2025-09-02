# app/routers/auth.py  (Flask blueprint)
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
from jose import jwt

# استفاده مستقیم از db ساخته‌شده در app/__init__.py
from app import db

bp = Blueprint("auth", __name__, url_prefix="/auth")

# تنظیمات token
ALGO = "HS256"
EXPIRE_MINUTES = 60

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    now = datetime.utcnow()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=EXPIRE_MINUTES)
    to_encode.update({"exp": int(expire.timestamp()), "iat": int(now.timestamp())})
    return jwt.encode(to_encode, current_app.config.get("SECRET_KEY"), algorithm=ALGO)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return check_password_hash(hashed_password, plain_password)

def get_user_by_username(username: str):
    from app.models import User
    return db.session.query(User).filter_by(username=username).first()


def decode_token(token: str):
    try:
        payload = jwt.decode(token, current_app.config.get("SECRET_KEY"), algorithms=[ALGO])
        return payload
    except Exception:
        return None

@bp.route("/token", methods=["POST"])
def token():

    # debug temporary — print incoming raw request to container stderr
    try:
        current_app.logger.debug("AUTH_DEBUG headers: %r", dict(request.headers))
        current_app.logger.debug("AUTH_DEBUG content_type: %r", request.content_type)
        current_app.logger.debug("AUTH_DEBUG raw body: %r", request.get_data(as_text=True))
    except Exception:
        pass


    # انتظار: JSON { "username": "...", "password": "..." }
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"detail":"username and password required"}), 400

    user = get_user_by_username(username)
    if not user:
        return jsonify({"detail":"invalid credentials"}), 401
    hashed = getattr(user, "hashed_password", None)
    if not hashed or not verify_password(password, hashed):
        return jsonify({"detail":"invalid credentials"}), 401

    token = create_access_token({"sub": username}, expires_delta=timedelta(minutes=EXPIRE_MINUTES))
    return jsonify({"access_token": token, "token_type": "bearer"})

@bp.route("/users/me", methods=["GET"])
def users_me():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"detail":"Missing token"}), 401
    token = auth.split(" ", 1)[1].strip()
    payload = decode_token(token)
    if not payload:
        return jsonify({"detail":"Invalid or expired token"}), 401
    username = payload.get("sub")
    user = get_user_by_username(username)
    if not user:
        return jsonify({"detail":"User not found"}), 404
    return jsonify({"username": user.username, "is_active": getattr(user, "is_active", True)})
