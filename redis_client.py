import redis
import json

r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
def save_battle_state(room_id: str, state: dict):
    r.set(f"battle:{room_id}:state", json.dumps(state))
def get_battle_state(room_id: str) -> dict | None:
    data = r.get(f"battle:{room_id}:state")
    if data:
        return json.loads(data)
    return None
def delete_battle_state(room_id: str):
    r.delete(f"battle:{room_id}:state")
