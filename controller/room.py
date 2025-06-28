from database.database import SessionLocal
from models.room import Room, RoomStatus
import datetime
import uuid
import time
from typing import Optional

def search_available_room(player_id, token) -> Optional[Room]:
    session = SessionLocal()
    try:
        room = session.query(Room).filter(
            Room.status == RoomStatus.waiting,
            Room.player1_id != player_id
        ).first()

        if not room:
            return None

        room.status = RoomStatus.ready
        room.player2_id = player_id
        room.player2_token = token
        session.commit()

        return Room(
            id=room.id,
            player1_id=room.player1_id,
            player1_token=room.player1_token,
            player2_id=room.player2_id,
            player2_token=room.player2_token,
            created_at=room.created_at,
            status=room.status
        )
    finally:
        session.close()
    
def create_room(player_id, token) -> Room:
    session = SessionLocal()
    try:
        room = Room(
            id=str(uuid.uuid4()),
            player1_id=player_id,
            player1_token=token,
            status=RoomStatus.waiting,
        )
        session.add(room)
        session.commit()

        if room.status == RoomStatus.waiting:
            start_time = time.time()
            while True:
                session.expire_all()
                session.refresh(room)
                if room.status == RoomStatus.ready:
                    break
                if time.time() - start_time > 300:
                    session.delete(room)
                    session.commit()
                    return None
                time.sleep(0.1)
        return room
    finally:
        session.close()

    