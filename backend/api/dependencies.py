"""
This package manages the dependencies for the API.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.core.security import verify_password
from backend.db.models import User
from backend.db.session import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    user = await verify_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def verify_token(db: Session, token: str):
    try:
        username, password = token.split(":")
        user = db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    except (ValueError, AttributeError):
        return None
