import json
from database.database import SessionLocal
from models.user import User

def handle_battle(body: dict, player_state: dict, enemy_state: dict | None) -> tuple[str, dict, dict | None]:
    try:
        x = int(body.get("x", 0))
        y = int(body.get("y", 0))
        action = int(body.get("action", 0))
        attack_type = int(body.get("attack_type", 0)) if body.get("attack_type") is not None else 0
        damage = int(body.get("damage", 0))
        flip = bool(body.get("flip", False))
        armor = max(1, int(body.get("armor", 1)))
    except (TypeError, ValueError):
        return json.dumps({
            "status": "fail",
            "message": "Data tidak valid"
        }), player_state or {}, enemy_state or {}

    # Update current player state
    player_state.update({
        "x": x,
        "y": y,
        "action": action,
        "attack_type": attack_type,
        "flip": flip,
        "armor": armor,
        "health": max(0, player_state.get("health", 100))  
    })

    if not enemy_state:
        return json.dumps({
            "status": "ok",
            "message": "Menunggu lawan...",
            "self": player_state,
            "enemy": {}
        }), player_state, enemy_state

    if attack_type in [1, 2]:
        dx = abs(player_state["x"] - enemy_state["x"])
        dy = abs(player_state["y"] - enemy_state["y"])
        if dx < 150 and dy < 100:
            effective_damage = max(1, damage - enemy_state.get("armor", 1))
            new_health = max(0, enemy_state.get("health", 100) - effective_damage)
            enemy_state["health"] = new_health

    return json.dumps({
        "status": "ok",
        "message": "Battle updated",
        "self": player_state,
        "enemy": enemy_state
    }), player_state, enemy_state

def get_player_data(user_id: int) -> dict | None:
    session = SessionLocal()
    
    user = session.query(User).filter(User.id == user_id).first()
    
    if user is None:
        session.close()
        return json.dumps({"status": "fail", "message": "User tidak ditemukan"})

    # Ambil hanya field yang diizinkan
    data = {
        "id": user.id,
        "nickname": user.nickname,
        "jumlah_match": user.jumlah_match,
        "winrate": user.winrate,
        "level": user.level,
        "exp": user.exp,
        "hp": user.hp,
        "attack": user.attack,
        "armor": user.armor,
        "token": user.token
    }

    session.close()
    return json.dumps({
        "status": "ok",
        "data": data
    })
    
def update_match(user_id: int, is_win: bool) -> str:
    MAX_EXP = 500
    session = SessionLocal()
    
    user = session.query(User).filter(User.id == user_id).first()
    
    if user is None:
        session.close()
        return json.dumps({"status": "fail", "message": "User tidak ditemukan"})

    jumlah_menang = user.winrate * user.jumlah_match // 100
    user.jumlah_match += 1
    if is_win:
        user.winrate = ((jumlah_menang + 1) * 100) // user.jumlah_match
        user.exp += 100
        if user.exp >= MAX_EXP:
            user.level += 1
            user.exp -= MAX_EXP
            user.hp += 10
            user.attack += 5
            user.armor += 1

    # Simpan perubahan ke database
    session.commit()
    session.close()

    return json.dumps({
        "status": "ok",
        "message": "Match updated successfully",
    })
    