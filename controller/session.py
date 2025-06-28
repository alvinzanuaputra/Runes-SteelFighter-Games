from database.database import SessionLocal
from models.session import Session
from typing import Optional
from datetime import datetime

def create_session(token: str, user_id: int) -> Session | None:
    db = SessionLocal()
    try:
        session = db.query(Session).filter(Session.user_id == user_id).first()
        if session and session.expired_at and session.expired_at < datetime.utcnow():
            db.delete(session)
            db.commit()
        session = Session(token=token, user_id=user_id)
        db.add(session)
        db.commit()
        return session
    finally:
        db.close()
        
def delete_session(token: str) -> bool:
    db = SessionLocal()
    try:
        session = db.query(Session).filter(Session.token == token).first()
        if not session:
            return False
        db.delete(session)
        db.commit()
        return True
    finally:
        db.close()
        
def get_session(token: str) -> Optional[Session]:
    db = SessionLocal()
    try:
        session_obj = db.query(Session).filter(Session.token == token).first()

        if session_obj is None:
            return None

        if session_obj.expired_at and session_obj.expired_at < datetime.utcnow():
            db.delete(session_obj)
            db.commit()
            return None

        return session_obj
    finally:
        db.close()
    