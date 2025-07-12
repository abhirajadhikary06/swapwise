from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_active_user
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.crud import create_user, get_user_by_auth0_id, update_user
from redis import Redis
import json

router = APIRouter()

redis = Redis(host="localhost", port=6379, decode_responses=True)

@router.post("/me", response_model=UserResponse)
async def create_or_get_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_auth0_id(db, user.auth0_id)
    if not db_user:
        db_user = create_user(db, user)
    return db_user

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_profile(user_data: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    updated_user = update_user(db, current_user.id, user_data.dict(exclude_unset=True))
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    redis.delete(f"user:{current_user.id}")
    return updated_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_profile(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    cache_key = f"user:{user_id}"
    cached_user = redis.get(cache_key)
    if cached_user:
        return json.loads(cached_user)
    user = db.query(User).filter(User.id == user_id, User.is_public == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found or profile is private")
    redis.setex(cache_key, 3600, json.dumps(UserResponse.from_orm(user).dict()))
    return user
