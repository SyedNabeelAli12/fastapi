from pydantic import BaseModel
from bson import ObjectId  

class User(BaseModel):
    name: str
    email: str
    age: int
    active:bool = True

class UserResponse(BaseModel):
    name: str
    email: str
    age: int
    active:bool
    id: str  

    class Config:
        json_encoders = { ObjectId: str }
