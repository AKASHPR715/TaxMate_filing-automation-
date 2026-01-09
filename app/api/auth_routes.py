from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from passlib.context import CryptContext
from app.db.connection import db
from app.db.models import User
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")  # Fallback for dev
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Models for Request Body
class UserSignup(BaseModel):
    username: str
    email: EmailStr
    pan: str
    fullname: str
    phone_num: str
    password: str

class UserLogin(BaseModel):
    identifier: str # username or email
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    
# Helpers
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Routes
@router.post("/signup", response_model=Token)
async def signup(user_data: UserSignup):
    database = db.get_db()
    users_collection = database["users"]

    # Check if user exists
    existing_user = await users_collection.find_one({
        "$or": [{"email": user_data.email}, {"username": user_data.username}]
    })
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)

    # Create User document
    # Note: Using 'username' field which was added to the model
    # Mapping 'phone_num' from request to 'phone_number' in model
    # Mapping 'fullname' from request to 'full_name' in model
    # Mapping 'pan' from request to 'pan_number' in model
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.fullname,
        phone_number=user_data.phone_num,
        pan_number=user_data.pan,
        password_hash=hashed_password,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Insert into DB
    result = await users_collection.insert_one(new_user.model_dump(by_alias=True, exclude=["id"]))
    
    # Create token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.username, "id": str(result.inserted_id), "username": new_user.username}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    database = db.get_db()
    users_collection = database["users"]

    # Find user by email or username
    user = await users_collection.find_one({
        "$or": [{"email": user_credentials.identifier}, {"username": user_credentials.identifier}]
    })

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.get("password_hash"):
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User has no password set (maybe created via other method)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(user_credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.get("username") or user.get("email"),
            "id": str(user["_id"]),
            "username": user.get("username")
        },
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Dependency for protected routes
# Dependency for protected routes
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.db.models import User, TokenBlacklist

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    database = db.get_db()
    
    # Check if token is blacklisted
    blacklist_collection = database["token_blacklist"]
    if await blacklist_collection.find_one({"token": token}):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been invalidated (logout)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("id")
        
        if username is None or user_id is None:
            raise credentials_exception
            
        # Return stateless user object
        # Using _id for compatibility with existing code
        return {"_id": user_id, "username": username}
        
    except JWTError:
        raise credentials_exception

from bson import ObjectId

@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user details.
    """
    database = db.get_db()
    users_collection = database["users"]
    
    try:
        user_id = ObjectId(current_user["_id"])
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
        
    user = await users_collection.find_one({"_id": user_id})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    # Serialize ObjectId to string
    user["_id"] = str(user["_id"])
    
    # Remove sensitive data
    user.pop("password_hash", None)
    
    return user

@router.post("/logout")
async def logout(
    current_user: dict = Depends(get_current_user),
    token_auth: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Logout user by blacklisting their token
    """
    database = db.get_db()
    blacklist_collection = database["token_blacklist"]
    
    token = token_auth.credentials
    
    # Check if already blacklisted (should be caught by get_current_user, but safe to check)
    if not await blacklist_collection.find_one({"token": token}):
        new_blacklist_entry = TokenBlacklist(token=token)
        await blacklist_collection.insert_one(new_blacklist_entry.model_dump(by_alias=True))
    
    return {"message": "Successfully logged out"}
