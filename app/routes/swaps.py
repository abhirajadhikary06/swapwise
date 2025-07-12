from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_active_user
from app.models import User, Swap
from app.schemas import SwapCreate, SwapResponse, FeedbackCreate, FeedbackResponse
from app.crud import create_swap, get_swaps_by_user, update_swap_status, create_feedback
from redis import Redis
import json

router = APIRouter()

redis = Redis(host="localhost", port=6379, decode_responses=True)

@router.post("/", response_model=SwapResponse)
async def create_swap_request(swap: SwapCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    if swap.requester_id == swap.receiver_id:
        raise HTTPException(status_code=400, detail="Cannot request swap with yourself")
    db_swap = create_swap(db, swap, current_user.id)
    redis.delete(f"swaps:{current_user.id}")
    return db_swap

@router.get("/me", response_model=list[SwapResponse])
async def get_my_swaps(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    cache_key = f"swaps:{current_user.id}"
    cached_swaps = redis.get(cache_key)
    if cached_swaps:
        return json.loads(cached_swaps)
    swaps = get_swaps_by_user(db, current_user.id)
    redis.setex(cache_key, 3600, json.dumps([SwapResponse.from_orm(swap).dict() for swap in swaps]))
    return swaps

@router.post("/{swap_id}/accept", response_model=SwapResponse)
async def accept_swap(swap_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    swap = db.query(Swap).filter(Swap.id == swap_id, Swap.receiver_id == current_user.id).first()
    if not swap or swap.status != "PENDING":
        raise HTTPException(status_code=400, detail="Invalid swap or not authorized")
    updated_swap = update_swap_status(db, swap_id, "ACCEPTED")
    redis.delete(f"swaps:{current_user.id}")
    redis.delete(f"swaps:{swap.requester_id}")
    return updated_swap

@router.post("/{swap_id}/reject", response_model=SwapResponse)
async def reject_swap(swap_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    swap = db.query(Swap).filter(Swap.id == swap_id, Swap.receiver_id == current_user.id).first()
    if not swap or swap.status != "PENDING":
        raise HTTPException(status_code=400, detail="Invalid swap or not authorized")
    updated_swap = update_swap_status(db, swap_id, "REJECTED")
    redis.delete(f"swaps:{current_user.id}")
    redis.delete(f"swaps:{swap.requester_id}")
    return updated_swap

@router.delete("/{swap_id}", response_model=SwapResponse)
async def cancel_swap(swap_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    swap = db.query(Swap).filter(Swap.id == swap_id, Swap.requester_id == current_user.id).first()
    if not swap or swap.status != "PENDING":
        raise HTTPException(status_code=400, detail="Invalid swap or not authorized")
    updated_swap = update_swap_status(db, swap_id, "CANCELLED")
    redis.delete(f"swaps:{current_user.id}")
    redis.delete(f"swaps:{swap.receiver_id}")
    return updated_swap

@router.post("/{swap_id}/feedback", response_model=FeedbackResponse)
async def submit_feedback(swap_id: int, feedback: FeedbackCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    swap = db.query(Swap).filter(Swap.id == swap_id).first()
    if not swap or swap.status != "ACCEPTED":
        raise HTTPException(status_code=400, detail="Invalid swap or not completed")
    if current_user.id not in [swap.requester_id, swap.receiver_id]:
        raise HTTPException(status_code=403, detail="Not authorized to provide feedback")
    db_feedback = create_feedback(db, feedback, current_user.id)
    return db_feedback
