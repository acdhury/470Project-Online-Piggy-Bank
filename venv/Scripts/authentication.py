from passlib.context import CryptContext
from fastapi import HTTPException, status
from models import User
import jwt

pawd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password):
    return pawd_context.hash(password)

async def verify_password(plain_password, hashed_password):
    return pawd_context.verify(plain_password, hashed_password)

async def authenticate_user(email, password):
    user = await User.get(email=email)

    if user and await verify_password(password, user.password_hash):
        return user
    return None

async def token_generator(email:str, password:str, secret_key: str):
    user = await authenticate_user(email, password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    token_data = {
        "id": user.id,
        "email": user.email
    }

    token = jwt.encode(token_data, secret_key)
    return token