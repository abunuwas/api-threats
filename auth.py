import requests
from fastapi import HTTPException
from jose import jwt, jws
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWSError, JWTError
from pydantic import BaseModel

jwks_endpoint = "https://apithreats.eu.auth0.com/.well-known/jwks.json"

jwks = requests.get(jwks_endpoint).json()["keys"]


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


class UserClaims(BaseModel):
    sub: str
