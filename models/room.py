from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from database.database import Base 
from datetime import datetime, timedelta
import enum

class RoomStatus(enum.Enum):
    waiting = "waiting"
    ready = "ready"
    expired = "expired"

class Room(Base):
    __tablename__ = 'rooms'

    id = Column(String, primary_key=True)
    player1_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    player1_token = Column(String, nullable=False)
    player2_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    player2_token = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(RoomStatus), default=RoomStatus.waiting)

    def is_expired(self):
        return datetime.utcnow() > self.created_at + timedelta(minutes=5)

    def is_waiting(self):
        return self.status == RoomStatus.waiting

    def is_ready(self):
        return self.status == RoomStatus.ready

    def join(self, player2_id, player2_token):
        self.player2_id = player2_id
        self.player2_token = player2_token
        self.status = RoomStatus.ready
