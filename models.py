from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql.sqltypes import DateTime
from datetime import datetime

Base = declarative_base()

# this class defines the models for user and applications
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    applications = relationship('Application', back_populates='user')


class Application(Base):
    __tablename__ = 'applications'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    status = Column(String(100), default='Pending')
    applied_on = Column(DateTime, default=datetime.utcnow)
    user = relationship('User', back_populates='applications')
