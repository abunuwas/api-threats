from typing import Annotated

import requests
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWSError, jwt, jws
from jose.exceptions import JWTClaimsError, JWTError, ExpiredSignatureError
from pydantic import BaseModel

security = HTTPBearer()


jwks_endpoint = "https://apithreats.eu.auth0.com/.well-known/jwks.json"

jwks = requests.get(jwks_endpoint).json()["keys"]


class UserClaims(BaseModel):
    sub: str


def find_public_key(kid):
    for key in jwks:
        if key["kid"] == kid:
            return key


def validate_token(token):
    try:
        unverified_headers = jws.get_unverified_header(token)
        return jwt.decode(
            token=token,
            key=find_public_key(unverified_headers["kid"]),
            audience="https://apithreats.com",
            algorithms="RS256",
        )
    except (
        ExpiredSignatureError,
        JWTError,
        JWTClaimsError,
        JWSError,
    ) as error:
        raise HTTPException(status_code=401, detail=str(error))


def authorize_access(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    token_payload = validate_token(credentials.credentials)
    return UserClaims(sub=token_payload["sub"])
