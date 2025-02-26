import jwt
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import HTTPException, Depends, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from environs import Env
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from db.connect import get_session
from schemas.token import TokenData
from db.operations import UserDO


env = Env()
env.read_env()


SECRET_KEY = env("SECRET_KEY")
SECRET_KEY_BOT = env("SECRET_KEY_BOT")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_hash_password(password):
    return pwd_context.hash(password)


async def authentificate_user(
    email: str, password: str, session: AsyncSession = Depends(get_session)
):
    user = await UserDO.get_by_email(email=email, session=session)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_session),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token expired",
    )
    payload = None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise expired_exception
    except jwt.PyJWTError:
        pass

    if not payload:
        try:
            payload = jwt.decode(token, SECRET_KEY_BOT, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise expired_exception
        except jwt.PyJWTError:
            raise credentials_exception
    email = payload.get("email")
    tg_id = payload.get("tg_id")
    if not email and not tg_id:
        raise credentials_exception
    token_data = TokenData(email=email, tg_id=tg_id)
    if token_data.email:
        user = await UserDO.get_by_email(email=token_data.email, session=session)
    else:
        user = await UserDO.get_by_tg_id(tg_id=token_data.tg_id, session=session)
    if user is None:
        raise credentials_exception
    return user
