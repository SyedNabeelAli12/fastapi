from fastapi import APIRouter, HTTPException, Depends,Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo.errors import DuplicateKeyError
from database import users_collection
from models.user_model import User, UserResponse
from schemas.userSchemas import UpdateUserRequest,DeleteUserRequest, SignInRequest
from common_functions.password_hash import hash_password
from common_functions.jwt import generate_tokens,decode_jwt
import jwt
from config import JWT_SK
import httpx

router = APIRouter()
security = HTTPBearer()
@router.on_event("startup")
async def create_unique_index():
    try:
        await users_collection.create_index("email", unique=True)
        await users_collection.create_index("password", unique=True)
        print("Unique index on 'email' created successfully.")
    except Exception as e:
        print("It may already exist. Error: {e}")

@router.post("/create_users/", response_model=UserResponse)
async def create_user(user: User):
    user_data = user.dict()
    password = hash_password(user_data["password"])
    user_data["password"] = password
    try:
        result = await users_collection.insert_one(user_data)
        user_data["id"] = str(result.inserted_id)
        return user_data
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Email already exists")
    
# To be in a separate file for the middleware access
def token_required(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        decoded_token = jwt.decode(token, JWT_SK, algorithms=["HS256"])
        return decoded_token  # Returns user payload (e.g., {"username": "test_user", "exp": 1716167932})
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/get_users/")
async def get_users(user: dict = Depends(token_required)):
    users_cursor = users_collection.find({"active": True})
    users = []
    async for user in users_cursor:
        user["id"] = str(user["_id"])
        del user["_id"]
        users.append(user)
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    return users

@router.post("/update_user/")
async def update_user(request: UpdateUserRequest):
    result = await users_collection.find_one_and_update(
        {"email": request.email}, {"$set": {"name": request.name}}, return_document=True
    )
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    result["id"] = str(result["_id"])
    del result["_id"]
    return result


@router.delete("/delete_user/")
async def update_user(request: DeleteUserRequest):
    result = await users_collection.find_one_and_update(
        {"email": request.email}, {"$set": {"active": False}}, return_document=True
    )
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    result["id"] = str(result["_id"])
    del result["_id"]
    return result
    

@router.post("/sign-in/")
async def sign_in(request: SignInRequest):
    result = await users_collection.find_one(
        {"email": request.email ,"password": hash_password(request.password) })
    if not result:
        raise HTTPException(status_code=402, detail="Invalid Username or Password")
    else:
    #   result["jwt"] =  generate_tokens(result["email"],result["role"])
        access_token, refresh_token = generate_tokens(result["email"])
    result["access_token"]= access_token
    # response = requests.post("http://127.0.0.1:8000/create_token/",json={"email":request.email,"refresh_token":refresh_token, "active":"1"})
    # print(response)
    async with httpx.AsyncClient() as client:
        response = await client.post("http://127.0.0.1:8000/token/create_token/", json={
        "email": request.email,
        "refresh_token": refresh_token,
        "active": "1"
    }, timeout=10)  # 10 seconds timeout
    print(response.status_code)

    result["id"] = str(result["_id"])
    
    del result["_id"]
    return result


# To be changed later. 
# Separate DB for tokens
# 
@router.post("/refresh")
def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    refresh_token = credentials.credentials
    decoded = decode_jwt(refresh_token, is_refresh=True)

    if isinstance(decoded, str):
        raise HTTPException(status_code=401, detail=decoded)  # Token expired or invalid
    
    email = decoded.get("email")
    
    # Ensure the refresh token is valid and exists in our store
    # if refresh_tokens_db.get(username) != refresh_token:
    #     raise HTTPException(status_code=403, detail="Invalid refresh token")

    # Generate a new access token
    new_access_token, _ = generate_tokens(email)

    return {"access_token": new_access_token}