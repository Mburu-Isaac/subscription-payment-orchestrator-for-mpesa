import jwt
from datetime import datetime, timedelta, timezone
from config import Config
import os
import uuid
from orchestrator.extensions import db
from orchestrator.models import RefreshTokens


class TokenManager:

    def __init__(self):
        self.private_key = Config.PRIVATE_KEY
        self.algorithm = os.environ.get("JWT_ALGORITHM")
        self.public_key = Config.PUBLIC_KEY

    def generate_access_token(self, user_id: int) -> str:
        
        issued_at = datetime.now()
        expires_at = issued_at + timedelta(minutes=15)

        payload = {
            "sub": str(user_id),
            "iat": issued_at,
            "exp": expires_at,
            "type": "access"
        }

        token = jwt.encode(
            payload=payload,
            key=self.private_key,
            algorithm=self.algorithm
        )

        return token, expires_at


    def verify_access_token(self, token: str) -> dict:
        
        try:
            payload = jwt.decode(
                token,
                public_key=self.public_key,
                algorithms=[self.algorithm]
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

    @staticmethod
    def store_refresh_token(
        user_id,
        token_jti,
        created_at,
        expires_at
    ):

        token = RefreshTokens(
            user_id=user_id,
            token_jti=token_jti,
            created_at=created_at,
            expires_at=expires_at
        )

        try:
            db.session.add(token)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def generate_refresh_token(self, user_id: int) -> dict:
        
        token_jti = str(uuid.uuid4())
        issued_at = datetime.now(timezone.utc)
        expires_at = datetime.now(timezone.utc) + timedelta(weeks=2)

        payload = {
            "sub": str(user_id),
            "jti": token_jti,
            "iat": issued_at,
            "exp": expires_at,
            "type": "refresh"
        }

        refresh_token = jwt.encode(
            payload=payload,
            key=self.private_key,
            algorithm=self.algorithm
        )

        self.store_refresh_token(
            user_id=user_id,
            token_jti=token_jti,
            created_at=issued_at,
            expires_at=expires_at
        )

        return refresh_token, token_jti

    def verify_refresh_token(self, token: str) -> dict:
        
        try:
            payload = jwt.decode(
                token,
                key=self.public_key,
                algorithms=[self.algorithm]
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")

        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

    def rotate_refresh_token(self, old_token: str):
        
        payload = self.verify_access_token(old_token)

        user_id = payload["sub"]
        old_token_jti = payload["jti"]

        try:
            token_record = db.session.execute(
                db.session.select(RefreshTokens).where(
                    RefreshTokens.token_jti == old_token_jti
                )
            ).scalar()

            if not token_record:
                raise Exception("Token not found")

            if token_record.revoked:
                raise Exception("Token already revoked. Re-use Detected")

            token_record.revoked = True
            db.session.commit()

            new_access_token = self.generate_access_token(user_id)
            new_refresh_token, new_jti = self.generate_access_token(user_id)

        except Exception:
            db.session.rollback()
            raise


