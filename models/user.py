from sqlalchemy import Column, Integer, String, ForeignKey
from database.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    password = Column(String)
    nickname = Column(String)
    jumlah_match = Column(Integer, default=0)
    winrate = Column(Integer, default=0)
    # last_login = Column(String, default='')
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    hp = Column(Integer, default=100)
    attack = Column(Integer, default=10)
    armor = Column(Integer, default=1)
    token = Column(String, unique=True, nullable=True)
