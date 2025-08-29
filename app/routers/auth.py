# app/routers/auth.py
from flask import Blueprint, request, jsonify, current_app
from jose import jwt
from werkzeug.security import check_password_hash
from app.models import User
from app import db
import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/token', methods=['POST'])
def token():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"error":"username and password required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error":"invalid credentials"}), 401

    if not check_password_hash(user.hashed_password, password):
        return jsonify({"error":"invalid credentials"}), 401

    payload = {
        "sub": user.id,
        "username": user.username,
        "exp": int((datetime.datetime.utcnow() + datetime.timedelta(hours=8)).timestamp())
    }
    token = jwt.encode(payload, current_app.config.get("SECRET_KEY", "your-secret-key"), algorithm="HS256")
    return jsonify({"access_token": token, "token_type": "bearer"})
