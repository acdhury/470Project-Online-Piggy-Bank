from tortoise.transactions import in_transaction
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models import User,user_pydantic, user_pydanticIn,SavingsPlan,SavingsPlan_PydanticOut
from fastapi import FastAPI, Depends, HTTPException, status
from tortoise.contrib.fastapi import register_tortoise
from authentication import get_hashed_password, token_generator
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
import secrets
from pydantic import BaseModel
#from tortoise import run_async,Tortoise
from fastapi.middleware.cors import CORSMiddleware 
app=FastAPI()
origin=[
    "http://localhost:3000"
]
app.add_middleware(
        CORSMiddleware,
        allow_origins=origin,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
)
class UserIn(BaseModel):
    username: str
    email: str
    password_hash: str 
    full_name: str 
    phone_number: str 
    address: str
    is_superuser: bool
    date_of_birth: str
@app.post("/register")
async def register(user_in: UserIn):
    # Extract the password from the input
    password = user_in.password_hash
    # Hash the password
    hashed_password = get_hashed_password(password)
    # Remove the password field from the input dictionary
    user_info = user_in.dict(exclude={"password"})
    # Assign the hashed password to the 'password_hash' field
    user_info["password_hash"] = hashed_password
    # Create the user with the modified input dictionary
    async with in_transaction():
        user_obj = await User.create(**user_info)
        response = await user_pydantic.from_tortoise_orm(user_obj)
        return {"status": "ok", "data": response}
@app.get("/admin{get_id}")
async def root():
    response=await user_pydantic.from_queryset(User.all())
    return {"status": "ok","data": response}
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/token')
@app.put("/admin/{get_id}")
async def update(get_id:int ,info: user_pydanticIn):
    user=await User.get(id=get_id)
    info=info.dict(exclude_unset=True)
    user.username=info["username"]
    user.email=info["email"]
    user.phone_number=info["phone_number"]
    user.address=info["address"]
    await user.save()
    response=await user_pydantic.from_tortoise_orm(user)
    return {"status": "ok","data": response}

@app.delete("/admin/{get_id}")
async def delete_info(get_id: int):
    user = await User.get(id=get_id)
    await user.delete()  
    return {"status": "ok", "data": None}
config_credential = {
    'SECRET': secrets.token_urlsafe(32)
}
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


@app.get("/savings_plans")
async def get_savings_plans():
    response = await SavingsPlan_PydanticOut.from_queryset(SavingsPlan.all())
    return {"status": "ok","data": response}
@app.post("/savings_plans")
async def plans(info:SavingsPlan_PydanticOut):
    plan=await SavingsPlan.create(**info.dict(exclude_unset=True))
    response=await SavingsPlan_PydanticOut.from_tortoise_orm(plan)
    return{"status":"ok","data":response}

register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)