# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from tortoise.contrib.fastapi import register_tortoise
from models import User, user_pydanticIn
from authentication import get_hashed_password, token_generator
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
import secrets

app = FastAPI()

# Define config_credential with secret key
config_credential = {
    'SECRET': secrets.token_urlsafe(32)
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/token')

@app.post('/token')
async def generate_token(request_form: OAuth2PasswordRequestForm = Depends()):
    # Use config_credential['SECRET'] to access the secret key
    token = await token_generator(request_form.username, request_form.password, config_credential['SECRET'])
    return {"access_token": token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # Use config_credential['SECRET'] to access the secret key
        payload = jwt.decode(token, config_credential['SECRET'], algorithms=['HS256'])
        user = await User.get(id=payload.get("id"))
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.post("/user/me")
async def user_login(current_user: User = Depends(get_current_user)):
    return {
        "status": "ok",
        "data": {
            "email": current_user.email
        }
    }

@app.get("/")
def index():
    return {"message": "Hello World"}

@app.post("/registration")
async def user_registration(user: user_pydanticIn):
    user_info = user.dict(exclude_unset=True)
    user_info["password"] = get_hashed_password(user_info["password"])
    user_obj = await User.create(**user_info)
    new_user = await user_pydanticIn.from_tortoise_orm(user_obj)
    return {
        "status": "ok",
        "data": f"hello {new_user.email}, check your inbox"
    }

register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)
