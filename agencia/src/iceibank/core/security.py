from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

import jwt

from iceibank.core.config import Settings
from iceibank.core.exceptions import NaoAutenticado


def hash_password(password: str, *, iterations: int = 310_000) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return "$".join(
        (
            "pbkdf2_sha256",
            str(iterations),
            base64.urlsafe_b64encode(salt).decode(),
            base64.urlsafe_b64encode(digest).decode(),
        )
    )


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations_text, salt_text, expected_text = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(salt_text)
        expected = base64.urlsafe_b64decode(expected_text)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(iterations_text))
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(actual, expected)


def create_access_token(subject: str, settings: Settings) -> tuple[str, int]:
    now = datetime.now(UTC)
    expires_in = settings.jwt_expiracao_minutos * 60
    payload = {
        "sub": subject,
        "iss": settings.jwt_issuer,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
    return token, expires_in


def decode_access_token(token: str, settings: Settings) -> str:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
            issuer=settings.jwt_issuer,
        )
        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject:
            raise NaoAutenticado("Token sem identificação de usuário.", "TOKEN_INVALIDO")
        return subject
    except NaoAutenticado:
        raise
    except jwt.ExpiredSignatureError as exc:
        raise NaoAutenticado("Token expirado.", "TOKEN_EXPIRADO") from exc
    except jwt.PyJWTError as exc:
        raise NaoAutenticado("Token inválido.", "TOKEN_INVALIDO") from exc
