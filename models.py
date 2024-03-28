import pydantic
from tortoise import Model, fields
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

class User(Model):
    id = fields.IntField(pk=True, index = True)
    email = fields.CharField(max_length=200, null = False, unique = True)
    password = fields.CharField(max_length=64, null = False)
    is_Verrified = fields.BooleanField(default=False)
    is_admin = fields.BooleanField(default=False)



user_pydantic = pydantic_model_creator(User, name="User", exclude = ("is_verified", ))
user_pydanticIn = pydantic_model_creator(User,name = "UserIn", exclude_readonly=True, exclude = ("is_verified", ))
user_pydanticOut = pydantic_model_creator(User, name = "UserOut", exclude=("password", "is_verified", "is_admin"))