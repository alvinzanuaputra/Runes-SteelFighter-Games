import json
from database.database import SessionLocal
from models.user import User

def handle_battle(body_raw: dict, player, enemy) -> tuple[str, dict, dict | None]:
    x = body_raw.get("x")
    y = body_raw.get("y")
    action = body_raw.get("action")
    attack_type = body_raw.get("attack_type")
    damage = body_raw.get("damage", 0)
    flip = body_raw.get("flip", False)
    armor = body_raw.get("armor", 1)

    try:
        x = int(x)
        y = int(y)
        action = int(action)
        attack_type = int(attack_type) if attack_type is not None else 0
        damage = int(damage)
        flip = bool(flip)
        armor = int(armor)
    except (TypeError, ValueError):
        my_state = player["state"] if player and "state" in player else {}
        return json.dumps({"status": "fail", "message": "Data tidak valid"}), my_state, None

    my_state = player["state"]
    my_state.update({
        "x": x,
        "y": y,
        "action": action,
        "attack_type": attack_type,
        "flip": flip,
        "armor": max(1, armor)
    })

    # Pertahankan health dari server, jangan terima dari client
    my_state["health"] = max(0, my_state.get("health", 100))

    if enemy is None or "state" not in enemy:
        return json.dumps({
            "status": "ok",
            "message": "Menunggu lawan...",
            "self": my_state,
            "enemy": {}
        }), my_state, None

    enemy_state = enemy["state"]

    # Proses serangan
    if attack_type in [1, 2]:
        distance_x = abs(my_state["x"] - enemy_state["x"])
        distance_y = abs(my_state["y"] - enemy_state["y"])
        if distance_x < 150 and distance_y < 100:
            effective_damage = max(1, damage - enemy_state.get("armor", 1))
            enemy_state["health"] = max(0, enemy_state.get("health", 100) - effective_damage)

    return json.dumps({
        "status": "ok",
        "message": "Battle updated",
        "self": my_state,
        "enemy": enemy_state
    }), my_state, enemy_state

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
    
def update_match(player_id: int, is_win: bool) -> str:
    MAX_EXP = 500
    session = SessionLocal()
    
    user = session.query(User).filter(User.id == player_id).first()
    
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