from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from app.core.config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Check if the plain password matches the hashed one in the database
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    # Generate a random salt and hash the password
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(subject: str | int) -> str:
    # Create the token payload with an expiration time and the user's ID (sub)
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    
    # Sign the token using our secret key
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt