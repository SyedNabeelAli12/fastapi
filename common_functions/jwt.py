import jwt
import datetime
import os
from config import JWT_SK

SECRET_KEY = os.getenv("SECRET_KEY", JWT_SK)
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", JWT_SK)

# Function to generate access and refresh tokens
def generate_tokens(email):
    access_payload = {
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15)  # Access token expires in 15 min
    }
    refresh_payload = {
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)  # Refresh token expires in 7 days
    }
    
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm="HS256")
    refresh_token = jwt.encode(refresh_payload, REFRESH_SECRET_KEY, algorithm="HS256")
    
    return access_token, refresh_token

# Function to decode JWT token
def decode_jwt(token, is_refresh=False):
    try:
        secret = REFRESH_SECRET_KEY if is_refresh else SECRET_KEY
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload  # Returns decoded token data
    except jwt.ExpiredSignatureError:
        return "Token has expired"
    except jwt.InvalidTokenError:
        return "Invalid token"


