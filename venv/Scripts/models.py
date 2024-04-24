from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel, Field
from datetime import date


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=100, unique=True)
    password_hash = fields.CharField(max_length=64)
    full_name = fields.CharField(max_length=255)
    date_of_birth = fields.DateField(null=True)
    address = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    is_superuser = fields.BooleanField(default=False)
    phone_number = fields.CharField(max_length=20, null=True)


class UserIn(BaseModel):
    username: str = Field(..., alias="username")
    email: str = Field(..., alias="email")
    password_hash: str = Field(..., alias="password")
    full_name: str = Field(..., alias="fullName")
    phone_number: str = Field(None, alias="phone_number")
    address: str = Field(None, alias="address")
    is_superuser: bool = Field(False, alias="is_superuser")
    date_of_birth: str = Field(None, alias="date_of_birth")

class UserOut(BaseModel):
    username: str = Field(..., alias="username")
    email: str = Field(..., alias="email")
    full_name: str = Field(..., alias="fullName")
    phone_number: str = Field(None, alias="phone_number")
    address: str = Field(None, alias="address")


class Deposit(Model):
    user = fields.ForeignKeyField('models.User', related_name='deposits')
    amount = fields.DecimalField(max_digits=12, decimal_places=2)
    deposit_date = fields.DateField(auto_now_add=True)
    
    class Meta:
        table = "deposits"

class Withdrawal(Model):
    user = fields.ForeignKeyField('models.User', related_name='withdrawals')
    amount = fields.DecimalField(max_digits=12, decimal_places=2)
    withdrawal_date = fields.DateField(auto_now_add=True)
    
    class Meta:
        table = "withdrawals"

user_pydantic = pydantic_model_creator(User, name="User", exclude = ("created_at"))
user_pydanticIn = pydantic_model_creator(User,name = "UserIn", exclude_readonly=True,exclude = ("created_at", ))
user_pydanticOut = pydantic_model_creator(User, name = "UserOut",exclude_readonly=True,exclude=("date_of_birth","full_name","email","address","phone_number","created_at", "is_superuser", "id"))
deposit_pydantic = pydantic_model_creator(Deposit, name="Deposit", exclude_readonly=True)
withdrawal_pydantic = pydantic_model_creator(Withdrawal, name="Withdrawal", exclude_readonly=True)
