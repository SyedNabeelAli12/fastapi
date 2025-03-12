from fastapi import FastAPI
from routes.users import router as user_router
from routes.refresh_token import router as token_router

app = FastAPI()

app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(token_router, prefix="/token", tags=["Token"])
# print(user_router.routes)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
