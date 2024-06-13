from datetime import datetime
import json
from fastapi import FastAPI, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from typing import List
from app.models.models import CardModel, MotorEventCreate, MotorEventModel, MotorPositionCreate, MotorPositionModel, PresenceDetectionCreate, PresenceDetectionModel, RfidReadCreate, RfidReadModel
from app.database.database_models import MotorEvent, MotorPosition, PresenceDetection, RfidRead, engine, Card

app = FastAPI()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

############################
@app.get("/cards/", response_model=List[CardModel])
def get_all_cards(db: Session = Depends(get_db)) -> CardModel:
    cards = db.query(Card).all()
    return cards

@app.get("/cards/{card_number}", response_model=bool)
def get_card_authorized(card_number: str, db: Session = Depends(get_db)) -> bool:
    db_card = db.query(Card).filter(Card.card_uid == card_number).first()
    return db_card.authorized

############################
@app.get("/motor_events/", response_model=List[MotorEventModel])
def get_all_motor_events(db: Session = Depends(get_db)) -> List[MotorEventModel]:
    events = db.query(MotorEvent).all()
    return events

@app.post("/motor_events/", response_model=MotorEventModel)
def create_motor_event(event_data: MotorEventCreate, db: Session = Depends(get_db)) -> MotorEventModel:
    db_event = MotorEvent(action=event_data.action, timestamp=datetime.now())

    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    return db_event

############################
@app.get("/motor_position/", response_model=List[MotorPositionModel])
def get_all_motor_events(db: Session = Depends(get_db)) -> List[MotorPositionModel]:
    events = db.query(MotorPosition).all()
    return events

@app.post("/motor_position/", response_model=MotorPositionModel)
def create_motor_event(event_data: MotorPositionCreate, db: Session = Depends(get_db)) -> MotorPositionModel:
    db_event = MotorPosition(position=event_data.position, timestamp=datetime.now())

    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    return db_event

############################
@app.get("/presence_detections/", response_model=List[PresenceDetectionModel])
def get_all_presence_detections(db: Session = Depends(get_db)) -> List[PresenceDetectionModel]:
    detections = db.query(PresenceDetection).all()
    return detections

@app.post("/presence_detections/", response_model=PresenceDetectionModel)
def create_presence_detection(detection_data: PresenceDetectionCreate, db: Session = Depends(get_db)) -> PresenceDetectionModel:
    db_detection = PresenceDetection(distance=detection_data.distance, timestamp=datetime.now())

    db.add(db_detection)
    db.commit()
    db.refresh(db_detection)

    return db_detection

############################
@app.get("/rfid_reads/")
def get_all_rfid_reads(db: Session = Depends(get_db)):
    reads = db.query(RfidRead).all()
    gros_dict = jsonable_encoder(reads)
    
    return json.dumps(gros_dict)

@app.post("/rfid_reads/", response_model=RfidReadModel)
def create_rfid_read(read_data: RfidReadCreate, db: Session = Depends(get_db)) -> RfidReadModel:
    db_read = RfidRead(card_uid=read_data.card_uid, timestamp=datetime.now(), authorized=read_data.authorized)

    db.add(db_read)
    db.commit()
    db.refresh(db_read)

    return db_read

