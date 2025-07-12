from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_admin_user
from app.models import User, Skill, Swap
from app.schemas import AdminMessage, ReportResponse
from app.crud import get_user_report, update_user, update_swap_status
from redis import Redis
import json

router = APIRouter()

redis = Redis(host="localhost", port=6379, decode_responses=True)

@router.post("/reject-skill/{skill_id}")
async def reject_skill(skill_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    db.delete(skill)
    db.commit()
    redis.delete(f"user_skills:{skill.user_id}")
    redis.delete(f"search_skills:{skill.skill_name.lower()}")
    return {"message": "Skill rejected and deleted"}

@router.post("/ban-user/{user_id}")
async def ban_user(user_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    update_user(db, user_id, {"is_public": False})
    redis.delete(f"user:{user_id}")
    return {"message": "User banned (profile set to private)"}

@router.get("/swaps", response_model=list[SwapResponse])
async def get_all_swaps(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    swaps = db.query(Swap).all()
    return swaps

@router.post("/message", response_model=AdminMessage)
async def send_platform_message(message: AdminMessage, current_admin: User = Depends(get_current_admin_user)):
    # In a real application, this would integrate with a notification system
    return {"message": f"Platform message sent: {message.message}"}

@router.get("/report/{user_id}", response_model=ReportResponse)
async def get_user_report(user_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    report = get_user_report(db, user_id)
    if not report:
        raise HTTPException(status_code=404, detail="User not found")
    return report
