# ─────────────────────────────────────────────
#  routes/auth.py — FastAPI Auth Endpoints
# ─────────────────────────────────────────────
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from database.db import get_db
from database import crud
from auth.jwt_handler import create_access_token
from auth.auth_service import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    email: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, req.email):
        raise HTTPException(status_code=400, detail="Email already registered.")
    if len(req.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")
    hashed = hash_password(req.password)
    user = crud.create_user(db, req.name, req.email, hashed)
    return {"message": "Registration successful!", "user_id": user.id}


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, req.email)
    if not user or not verify_password(req.password, user.hashed_password or ""):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return TokenResponse(access_token=token, user_id=user.id, name=user.name, email=user.email)


@router.get("/me")
def get_me(db: Session = Depends(get_db), token: str = ""):
    from auth.jwt_handler import decode_user_id
    user_id = decode_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"id": user.id, "name": user.name, "email": user.email, "points": user.total_points, "streak": user.streak}
