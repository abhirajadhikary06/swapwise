from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import User, Skill, Swap, Feedback
from app.schemas import UserCreate, SkillCreate, SwapCreate, FeedbackCreate

def create_user(db: Session, user: UserCreate):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_auth0_id(db: Session, auth0_id: str):
    return db.query(User).filter(User.auth0_id == auth0_id).first()

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def update_user(db: Session, user_id: int, user_data: dict):
    db_user = get_user(db, user_id)
    if db_user:
        for key, value in user_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def create_skill(db: Session, skill: SkillCreate, user_id: int):
    db_skill = Skill(**skill.dict(), user_id=user_id)
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill

def get_skills_by_user(db: Session, user_id: int):
    return db.query(Skill).filter(Skill.user_id == user_id).all()

def search_skills(db: Session, skill_name: str):
    return db.query(Skill).join(User).filter(
        Skill.skill_name.ilike(f"%{skill_name}%"),
        User.is_public == True
    ).all()

def create_swap(db: Session, swap: SwapCreate, requester_id: int):
    db_swap = Swap(**swap.dict(), requester_id=requester_id, status="PENDING")
    db.add(db_swap)
    db.commit()
    db.refresh(db_swap)
    return db_swap

def get_swaps_by_user(db: Session, user_id: int):
    return db.query(Swap).filter(
        or_(Swap.requester_id == user_id, Swap.receiver_id == user_id)
    ).all()

def update_swap_status(db: Session, swap_id: int, status: str):
    db_swap = db.query(Swap).filter(Swap.id == swap_id).first()
    if db_swap:
        db_swap.status = status
        db.commit()
        db.refresh(db_swap)
    return db_swap

def create_feedback(db: Session, feedback: FeedbackCreate, reviewer_id: int):
    db_feedback = Feedback(**feedback.dict(), reviewer_id=reviewer_id)
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

def get_user_report(db: Session, user_id: int):
    user = get_user(db, user_id)
    if not user:
        return None
    skills_offered = db.query(Skill).filter(Skill.user_id == user_id, Skill.is_offered == True).all()
    skills_wanted = db.query(Skill).filter(Skill.user_id == user_id, Skill.is_offered == False).all()
    swaps = get_swaps_by_user(db, user_id)
    feedback = db.query(Feedback).join(Swap).filter(
        or_(Swap.requester_id == user_id, Swap.receiver_id == user_id)
    ).all()
    return {
        "user_id": user.id,
        "name": user.name,
        "skills_offered": skills_offered,
        "skills_wanted": skills_wanted,
        "swaps": swaps,
        "feedback": feedback
    }
