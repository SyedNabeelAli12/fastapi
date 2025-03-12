from pydantic import BaseModel

class VerifyToken(BaseModel):
    email: str
