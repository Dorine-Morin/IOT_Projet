from datetime import datetime
from pydantic import BaseModel

############################################################
class CardBase(BaseModel):
    card_uid: str
    authorized: bool

class CardCreate(CardBase):
    pass

class CardModel(CardBase):
    pass

    class Config:
        orm_mode = True

############################################################
class MotorEventBase(BaseModel):
    action: str

class MotorEventCreate(MotorEventBase):
    pass

class MotorEventModel(MotorEventBase):
    timestamp: datetime    

    class Config:
        orm_mode = True

############################################################
class MotorPositionBase(BaseModel):
    position: int

class MotorPositionCreate(MotorPositionBase):
    pass

class MotorPositionModel(MotorPositionBase):
    timestamp: datetime

    class Config:
        orm_mode = True

############################################################
class PresenceDetectionBase(BaseModel):
    distance: float
    
class PresenceDetectionCreate(PresenceDetectionBase):
    pass

class PresenceDetectionModel(PresenceDetectionBase):
    timestamp: datetime 

    class Config:
        orm_mode = True

############################################################
class RfidReadBase(BaseModel):
    card_uid: str
    authorized: bool

class RfidReadCreate(RfidReadBase):
    pass

class RfidReadModel(RfidReadBase):
    timestamp: datetime

    class Config:
        orm_mode = True