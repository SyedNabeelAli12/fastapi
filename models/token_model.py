from pydantic import BaseModel
from bson import ObjectId  

class RefreshToken(BaseModel):
    email: str
    refresh_token:str
    active:str

class RefreshTokenResponse(BaseModel):
    email: str
    id: str 
    active: str 
    refresh_token:str
    class Config:
        json_encoders = { ObjectId: str }
