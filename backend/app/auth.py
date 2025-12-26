"""
Auth0 JWT Authentication for FastAPI.

Provides JWT token verification using Auth0's JWKS endpoint.
"""

import json
import os
from typing import Optional
from urllib.request import urlopen

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError

# Auth0 Configuration
AUTH0_DOMAIN = "instalily.us.auth0.com"
API_AUDIENCE = "https://instalily.us.auth0.com/api/v2/"
ALGORITHMS = ["RS256"]

# Security scheme for Bearer token
security = HTTPBearer()


class AuthError(Exception):
    """Exception raised for authentication errors."""
    def __init__(self, error: dict, status_code: int):
        self.error = error
        self.status_code = status_code


def get_jwks():
    """Fetch JSON Web Key Set from Auth0."""
    jsonurl = urlopen(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
    return json.loads(jsonurl.read())


def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    FastAPI dependency that verifies JWT tokens from Auth0.

    Returns the decoded token payload if valid.
    Raises HTTPException if invalid.
    """
    # Development mode bypass
    if os.environ.get("DEV_MODE", "").upper() == "TRUE":
        return {"sub": "dev_user", "email": "dev@instalily.ai"}

    token = credentials.credentials

    try:
        # Fetch JWKS from Auth0
        jwks = get_jwks()

        # Get unverified header to find the key ID
        unverified_header = jwt.get_unverified_header(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "invalid_header",
                "description": "Invalid header. Unable to parse authentication token."
            }
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "jwks_error",
                "description": "Unable to fetch JWKS from Auth0."
            }
        )

    # Find the RSA key matching the token's key ID
    rsa_key = {}
    for key in jwks.get("keys", []):
        if key.get("kid") == unverified_header.get("kid"):
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
            break

    if not rsa_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "invalid_header",
                "description": "Unable to find appropriate key."
            }
        )

    # Verify and decode the token
    try:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "token_expired",
                "description": "Token has expired."
            }
        )
    except jwt.JWTClaimsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "invalid_claims",
                "description": "Incorrect claims. Please check the audience and issuer."
            }
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "invalid_token",
                "description": "Unable to parse authentication token."
            }
        )


def get_current_user(token_payload: dict = Depends(verify_jwt)) -> dict:
    """
    FastAPI dependency that returns the current authenticated user.

    Use this when you need access to the user info in your endpoint.
    """
    return token_payload
