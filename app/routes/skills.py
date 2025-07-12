from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_active_user
from app.models import User
from app.schemas import SkillCreate, SkillResponse
from app.crud import create_skill, get_skills_by_user, search_skills
from redis import Redis
import json

router = APIRouter()

redis = Redis(host="localhost", port=6379, decode_responses=True)

@router.post("/", response_model=SkillResponse)
async def create_skill(skill: SkillCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_skill = create_skill(db, skill, current_user.id)
    redis.delete(f"user_skills:{current_user.id}")
    return db_skill

@router.get("/me", response_model=list[SkillResponse])
async def get_my_skills(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    cache_key = f"user_skills:{current_user.id}"
    cached_skills = redis.get(cache_key)
    if cached_skills:
        return json.loads(cached_skills)
    skills = get_skills_by_user(db, current_user.id)
    redis.setex(cache_key, 3600, json.dumps([SkillResponse.from_orm(skill).dict() for skill in skills]))
    return skills

@router.get("/search", response_model=list[SkillResponse])
async def search_skills_by_name(skill_name: str, db: Session = Depends(get_db)):
    cache_key = f"search_skills:{skill_name.lower()}"
    cached_skills = redis.get(cache_key)
    if cached_skills:
        return json.loads(cached_skills)
    skills = search_skills(db, skill_name)
    redis.setex(cache_key, 3600, json.dumps([SkillResponse.from_orm(skill).dict() for skill in skills]))
    return skills
