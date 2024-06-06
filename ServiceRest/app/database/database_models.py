from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://avnadmin:AVNS_PjGuiaMWF8uBID8ilXp@mysql-3deb058a-morindorine-c300.d.aivencloud.com:14176/defaultdb?ssl-mode=REQUIRED"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Card(Base):
    __tablename__ = 'cards'
    id = Column(Integer, primary_key=True, index=True)
    card_uid = Column(String, unique=True, index=True)
    authorized = Column(Boolean)

class MotorEvent(Base):
    __tablename__ = 'motor_events'
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime)
    action = Column(String)

class MotorPosition(Base):
    __tablename__ = 'motor_position'
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime)
    position = Column(Integer)

class PresenceDetection(Base):
    __tablename__ = 'presence_detections'
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime)
    distance = Column(Float)

class RfidRead(Base):
    __tablename__ = 'rfid_reads'
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime)
    card_uid = Column(String)
    authorized = Column(Boolean)
