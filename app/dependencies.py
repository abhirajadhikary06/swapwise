from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app.config import Config
from app.auth import get_current_user
from app.models import User
from app.crud import get_user_by_auth0_id

engine = create_engine(Config.DATABASE_URL)

def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()

async def get_current_active_user(db: Session = Depends(get_db), payload: dict = Depends(get_current_user)):
    user = get_user_by_auth0_id(db, payload.get("sub"))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

async def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized as admin")
    return current_user
