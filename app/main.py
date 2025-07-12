
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import Config
from app.routes import users, skills, swaps, admin

app = FastAPI(title="SwapWise API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://{Config.APP_HOST}:{Config.APP_PORT}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(skills.router, prefix="/skills", tags=["skills"])
app.include_router(swaps.router, prefix="/swaps", tags=["swaps"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

@app.get("/")
async def root():
    return {"message": "Welcome to SwapWise API"}
