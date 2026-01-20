from fastapi import APIRouter, HTTPException, status
from schemas.user import CreateUserInput,LoginInput,UserLoginOutput,UserRegisterOutput,UserDeleteOutput,ForgotPasswordInput,ResetPasswordInput,ResetPasswordOutput,ForgotPasswordOutput
from sqlalchemy.orm import Session
from fastapi import Depends
from db.session import get_db  
from middleware.auth import get_current_user
from models.user import User
from datetime import datetime, timedelta
from jose import jwt
from uuid import UUID
import bcrypt
import os
from utils.email import send_template_email

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserRegisterOutput)
def get_me(current_user = Depends(get_current_user)):
    return {"user":current_user , "message":"User fetched successfully" }

@router.post("/register", response_model=UserRegisterOutput)
def createUser(createUserInput: CreateUserInput, db: Session = Depends(get_db)):
    existingUser = db.query(User).filter(User.email == createUserInput.email).first()

    if existingUser:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    createUserInput.password = hash_password(createUserInput.password)

    db_user = User(**createUserInput.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"user":db_user, "message":"User created successfully" }


@router.post("/login", response_model=UserLoginOutput)
def login(loginInput: LoginInput, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == loginInput.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    isPasswordMatched=verify_password(loginInput.password, user.password)
    
    if not isPasswordMatched:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
                                                      
    return {"user":user, "message":"Login Successfully", "token": create_access_token({"sub": str(user.id),"email": user.email}) }

@router.post("/forgot-password",response_model=ForgotPasswordOutput)
def forgot_password(
    payload: ForgotPasswordInput,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == payload.email).first()

    # Security: do NOT reveal whether user exists
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    token = create_access_token({"sub":str(user.id)})
    reset_link = f"https://yourfrontend.com/reset-password?token={token}"

    send_template_email(
        to_email=user.email,
        template_id=os.getenv("FORGET_PASSWORD_TEMPLATE_ID"),
        dynamic_data={
            "first_name": user.firstName,
            "reset_link": reset_link,
        },
    )

    return {"message": "If the email exists, a reset link has been sent."}

@router.post("/reset-password", response_model=ResetPasswordOutput)
def reset_password(
    payload: ResetPasswordInput,
    db: Session = Depends(get_db),
):
    payload = jwt.decode(payload.token, os.getenv("SECRET_KEY"), algorithms=os.getenv("ALGORITHM"))
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    user = db.get(User, UUID(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
   
    user.password = hash_password(payload.new_password)
    db.commit()

    return {"message": "Password reset successfully"}

@router.delete("/{id}", response_model=UserDeleteOutput)
def deleteUser(id: UUID, db: Session = Depends(get_db)):
    user = db.get(User, id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db.delete(user)
    db.commit()                                                
    return {"message":"User Deleted Successfully"}

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))