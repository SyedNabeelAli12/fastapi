from fastapi import APIRouter, HTTPException
from pymongo.errors import DuplicateKeyError
from database import users_collection
from models.userModels import User, UserResponse
from schemas.userSchemas import UpdateUserRequest,DeleteUserRequest

router = APIRouter()

@router.on_event("startup")
async def create_unique_index():
    try:
        await users_collection.create_index("email", unique=True)
        print("Unique index on 'email' created successfully.")
    except Exception as e:
        print("It may already exist. Error: {e}")

@router.post("/create_users/", response_model=UserResponse)
async def create_user(user: User):
    user_data = user.dict()
    try:
        result = await users_collection.insert_one(user_data)
        user_data["id"] = str(result.inserted_id)
        return user_data
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Email already exists")

@router.get("/get_users/")
async def get_users():
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
