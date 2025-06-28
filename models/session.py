from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from datetime import datetime, timedelta
from sqlalchemy.dialects.mysql import JSON
from database.database import Base  
from sqlalchemy.sql import func

class Session(Base):
    __tablename__ = 'sessions'

    token = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    expired_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=1))
