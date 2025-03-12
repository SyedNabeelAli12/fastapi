from fastapi import APIRouter, HTTPException, Depends,Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo.errors import DuplicateKeyError
from database import token_collection
from models.token_model import RefreshToken, RefreshTokenResponse
from schemas.tokenSchemas import VerifyToken
from common_functions.password_hash import hash_password
from common_functions.jwt import generate_tokens,decode_jwt
import jwt
from config import JWT_SK

router = APIRouter()
security = HTTPBearer()
@router.on_event("startup")
async def create_unique_index():
    try:
        await token_collection.create_index("email", unique=True)
        print("Unique index on 'email' created successfully.")
    except Exception as e:
        print("It may already exist. Error: {e}")



@router.post("/create_token/", response_model=RefreshTokenResponse)
async def create_user(token: RefreshToken):
    token_data = token.dict()
    try:
        result = await token_collection.insert_one(token_data)
        token_data["id"] = str(result.inserted_id)
        return token_data
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Email already exists")
    
# To be in a separate file for the middleware access
# @router.post("/verify_token/", email)
def token_required(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        decoded_token = jwt.decode(token, JWT_SK, algorithms=["HS256"])
        return decoded_token  # Returns user payload (e.g., {"username": "test_user", "exp": 1716167932})
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# To be changed later. 
# Separate DB for tokens
# 
@router.post("/refresh")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    refresh_token = credentials.credentials
    decoded = decode_jwt(refresh_token, is_refresh=True)

    if isinstance(decoded, str):
        raise HTTPException(status_code=401, detail=decoded)  # Token expired or invalid
    
    email = decoded.get("email")
    
    # Ensure the refresh token is valid and exists in our store

    token = await token_collection.find_one({"email":email})
    if token != refresh_token:
        raise HTTPException(status_code=403, detail="Invalid refresh token")

    # Generate a new access token
    new_access_token, _ = generate_tokens(email)

    return {"access_token": new_access_token}