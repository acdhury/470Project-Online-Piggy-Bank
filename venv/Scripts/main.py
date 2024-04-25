from datetime import datetime, timedelta
from tortoise.transactions import in_transaction
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import FastAPI, Depends, HTTPException, status, Request, Form 
from tortoise.contrib.fastapi import register_tortoise
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from authentication import get_hashed_password, token_generator
from models import *
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
import secrets
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware 




app=FastAPI()

origin=[
    "http://localhost:3000"
]

templates = Jinja2Templates(directory="frontend/templates")

app.add_middleware(
        CORSMiddleware,
        allow_origins=origin,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
)



@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}


@app.get("/register", response_class=HTMLResponse)
async def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request":request})

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


@app.get("/login", response_class=HTMLResponse)
async def get_login(request:Request):
    return templates.TemplateResponse("login.html",{"request":request})


@app.post('/token')
async def generate_token(request_form: OAuth2PasswordRequestForm = Depends()):
    # Use config_credential['SECRET'] to access the secret key
    token = await token_generator(request_form.username, request_form.password, config_credential['SECRET'])
    return {"access_token": token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
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


@app.get("/homepage")
async def homepage(current_user: User = Depends(get_current_user)):
    # Calculate total balance
    user_deposits_list = await Deposit.filter(user=current_user).values('amount')
    total_balance = sum([item['amount'] for item in user_deposits_list])

    # Fetch all user's deposits
    user_deposits = await Deposit.filter(user=current_user)

    deposits_data = []
    for deposit in user_deposits:
        deposits_data.append({
            "amount": deposit.amount,
            "deposit_date": deposit.deposit_date
        })

    # User details
    user_details = {
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "phone_number": current_user.phone_number,
        "address": current_user.address,
        "date_of_birth": str(current_user.date_of_birth) if current_user.date_of_birth else None,
        "is_superuser": current_user.is_superuser
    }

    return {
        "status": "ok",
        "user_details": user_details,
        "bank_balance": total_balance,
        "deposits": deposits_data
    }


@app.get("/add-money", response_class=HTMLResponse)
async def get_add_money(request:Request):
    return templates.TemplateResponse("add-money.html", {"request":request})


@app.post("/add_money")
async def add_money(amount: float, current_user: User = Depends(get_current_user)):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount should be positive")

    # Get today's date
    today_date = datetime.now().date()

    # Create a new deposit record with today's date
    deposit = await Deposit.create(
        user=current_user,
        amount=amount,
        deposit_date=today_date  # Set today's date
    )

    # Calculate new balance
    user_deposits_list = await Deposit.filter(user=current_user).values('amount')
    new_balance = sum([item['amount'] for item in user_deposits_list])

    return {
        "status": "ok",
        "data": {
            "main_balance": new_balance,
            "deposit_id": deposit.id
        }
    }


@app.get("/withdraw", response_class=HTMLResponse)
async def withdraw(request:Request):
    return templates.TemplateResponse("withdraw.html", {"request":request})


@app.post("/withdraw_money")
async def withdraw_money(amount: float, current_user: User = Depends(get_current_user)):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount should be positive")

    # Check if user has sufficient balance
    user_deposits_list = await Deposit.filter(user=current_user).order_by('-deposit_date').values('amount', 'deposit_date')
    
    if not user_deposits_list:
        raise HTTPException(status_code=400, detail="No deposits found")

    last_deposit_date = user_deposits_list[0]['deposit_date']
    today_date = datetime.now().date()

    # Check if last deposit is less than 7 days old
    if (today_date - last_deposit_date).days < 7:
        raise HTTPException(status_code=400, detail="Cannot withdraw as last deposit is less than 7 days old")

    total_balance = sum([item['amount'] for item in user_deposits_list])

    if total_balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # Create a new withdrawal record with today's date
    withdrawal = await Withdrawal.create(
        user=current_user,
        amount=amount,
        withdrawal_date=today_date  
    )

    # Calculate new balance after withdrawal
    new_balance = float(total_balance) - float(amount)

    return {
        "status": "ok",
        "data": {
            "main_balance": new_balance,
            "withdrawal_id": withdrawal.id
        }
    }




register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)