from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel, Field
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

# Define other Pydantic models similarly

class Transaction(Model):
    id = fields.IntField(pk=True)
    #tran_id=fields.ForeignKeyField('models.User',related_name='transaction')
    user = fields.ForeignKeyField('models.User', related_name='transaction',on_delete=fields.CASCADE)
    amount = fields.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = fields.CharField(max_length=10)
    transaction_time = fields.DatetimeField(auto_now_add=True)
    class Meta:
        ordering = ['-transaction_time']
#class transaction_details(Model):
 #   bank_name=
  #  acc_no=

class SavingsPlan(Model):
    name = fields.CharField(max_length=100)
    description = fields.TextField()
    withdrawal_period = fields.IntField()  # Withdrawal period in days

class UserSavings(Model):
    id = fields.IntField(pk=True)
    #sav_id=fields.ForeignKeyField('models.User',related_name='UserSavings')
    user = fields.ForeignKeyField('models.User', related_name='User_Savings',on_delete=fields.CASCADE)
    plan = fields.ForeignKeyField('models.SavingsPlan', related_name='UserSavings')
    amount = fields.DecimalField(max_digits=12, decimal_places=2)
    start_date = fields.DateField(auto_now_add=True)
    end_date = fields.DateField(null=True)  # Date when the plan ends
    class Meta:
        ordering = ['-start_date']

user_pydantic = pydantic_model_creator(User, name="User", exclude = ("created_at"))
user_pydanticIn = pydantic_model_creator(User,name = "UserIn", exclude_readonly=True,exclude = ("created_at", ))
user_pydanticOut = pydantic_model_creator(User, name = "UserOut",exclude_readonly=True,exclude=("date_of_birth","full_name","email","address","phone_number","created_at", "is_superuser", "id"))
SavingsPlan_PydanticOut = pydantic_model_creator(SavingsPlan, name="SavingsPlan",exclude_readonly=True)
Transaction_Pydantic = pydantic_model_creator(Transaction, name="Transaction",exclude_readonly=True)
UserSavings_Pydantic = pydantic_model_creator(UserSavings, name="UserSavings",exclude_readonly=True)
