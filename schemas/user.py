from pydantic import BaseModel, EmailStr
from uuid import UUID

class CreateUserInput(BaseModel):
    email: EmailStr
    firstName: str
    lastName: str
    password: str

class LoginInput(BaseModel):
    email: EmailStr
    password: str

class UserOutput(BaseModel):
    id: UUID
    email: EmailStr
    firstName: str
    lastName: str
    is_active: bool

    class Config:
        from_attributes = True

class UserLoginOutput(BaseModel):
    user: UserOutput
    token: str
    message:str

    class Config:
        from_attributes = True

class UserRegisterOutput(BaseModel):
    user: UserOutput
    message: str

    class Config:
        from_attributes = True

class UserDeleteOutput(BaseModel):
    message: str

class ForgotPasswordInput(BaseModel):
    email: EmailStr

class ResetPasswordInput(BaseModel):
    email: EmailStr
    token: str
    new_password: str

class ResetPasswordOutput(UserDeleteOutput):
    pass

class ForgotPasswordOutput(UserDeleteOutput):
    pass