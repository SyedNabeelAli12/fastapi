from pydantic import BaseModel

class UpdateUserRequest(BaseModel):
    name: str
    email: str

class DeleteUserRequest(BaseModel):
    email: str

class SignInRequest(BaseModel):
    email: str
    password:str