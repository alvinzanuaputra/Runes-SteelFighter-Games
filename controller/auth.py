import bcrypt
from database.database import SessionLocal
from models.user import User
import uuid
import json

import json

def register(body_raw: str) -> str:
    session = SessionLocal()

    try:
        data = json.loads(body_raw)
    except json.JSONDecodeError:
        return json.dumps({"status": "fail", "message": "Body bukan JSON valid"})

    username = data.get("username")
    password = data.get("password")
    nickname = data.get("nickname")

    if not username or not password or not nickname:
        return json.dumps({"status": "fail", "message": "Username, password, dan nickname wajib diisi"})

    if session.query(User).filter(User.username == username).first() is not None:
        session.close()
        return json.dumps({"status": "fail", "message": "Username sudah terdaftar"})
    if session.query(User).filter(User.nickname == nickname).first() is not None:
        session.close()
        return json.dumps({"status": "fail", "message": "Nickname sudah terdaftar"})

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = User(username=username, password=hashed_password.decode('utf-8'), nickname=nickname)
    session.add(user)
    session.commit()
    session.close()

    return json.dumps({"status": "ok", "message": "Registrasi berhasil"})

def login(body_raw: str) -> tuple[str, dict | None]:
    try:
        data = json.loads(body_raw)
    except json.JSONDecodeError:
        return json.dumps({"status": "fail", "message": "Body bukan JSON valid"}), None

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return json.dumps({"status": "fail", "message": "Username dan password wajib diisi"}), None

    session = SessionLocal()
    user = session.query(User).filter(User.username == username).first()

    if user is None:
        session.close()
        return json.dumps({"status": "fail", "message": "Username tidak ditemukan"}), None

    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        session.close()
        return json.dumps({"status": "fail", "message": "Password salah"}), None

    # Ambil data yang dibutuhkan sebelum close
    user_id = user.id
    username = user.username

    generated_token = f"{user_id}-{uuid.uuid4().hex}"
    user.token = generated_token
    session.commit()
    session.close()

    session_player = {
        "token": generated_token,
        "player_id": user_id,
        "username": username,
        "state": {
            "x": 100 if user_id % 2 == 0 else 700,
            "y": 300,
            "health": 100,
            "action": 0,
            "attack_type": 0,
            "flip": user_id % 2 == 1
        }
    }

    return json.dumps({
        "status": "ok",
        "message": "Login berhasil",
        "token": generated_token,
        "player_id": user_id
    }), session_player

def logout(body_raw: str) -> tuple[str, dict | None]:
    try:
        data = json.loads(body_raw)
    except json.JSONDecodeError:
        return json.dumps({"status": "fail", "message": "Body bukan JSON valid"})

    token = data.get("token")

    if not token:
        return json.dumps({"status": "fail", "message": "Token tidak ditemukan dalam request"})

    session = SessionLocal()
    user = session.query(User).filter(User.token == token).first()

    if user is None:
        session.close()
        return json.dumps({"status": "fail", "message": "Token tidak valid"})

    user.token = None
    session.commit()
    session.close()

    return json.dumps({"status": "ok", "message": "Logout berhasil"}), token