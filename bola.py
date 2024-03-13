import os
import uuid
from typing import Annotated

import requests
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy import Uuid, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from starlette import status
from starlette.responses import RedirectResponse

from auth import validate_token, UserClaims

AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")

assert (
    AUTH0_CLIENT_SECRET is not None
), "AUTH0_CLIENT_SECRET environment variable needed."

server = FastAPI()


class Base(DeclarativeBase):
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)


class UserModel(Base):
    __tablename__ = "user"


class OrderModel(Base):
    __tablename__ = "order"

    user: Mapped[str]
    product: Mapped[str]
    quantity: Mapped[int]


class PlaceOrderSchema(BaseModel):
    product: str
    quantity: int


class GetOrderSchema(PlaceOrderSchema):
    id: uuid.UUID


class UserDetailsSchema(BaseModel):
    email: str
    password: str


class AuthorizationCode(BaseModel):
    code: str


engine = create_engine("sqlite:///bola.db")
Base.metadata.create_all(engine)
session_maker = sessionmaker(bind=engine)


@server.get("/login")
def register():
    return RedirectResponse(
        "https://apithreats.eu.auth0.com/authorize"
        "?response_type=code"
        "&client_id=QDg7IrUH8jJ27ibGDRaEG5qW24dGOeWH"
        "&redirect_uri=http://localhost:8000/token"
        "&scope=offline_access"
        "&audience=https://apithreats.com"
    )


@server.get("/token")
def get_access_token(code: str):
    payload = (
        "grant_type=authorization_code"
        "&client_id=QDg7IrUH8jJ27ibGDRaEG5qW24dGOeWH"
        f"&client_secret={AUTH0_CLIENT_SECRET}"
        f"&code={code}"
        "&redirect_uri=http://localhost:8000/token"
    )
    headers = {"content-type": "application/x-www-form-urlencoded"}
    response = requests.post(
        "https://apithreats.eu.auth0.com/oauth/token", payload, headers=headers
    )
    return response.json()["access_token"]


security = HTTPBearer()


def validate_access(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    token_payload = validate_token(credentials.credentials)
    return UserClaims(sub=token_payload["sub"])


@server.post(
    "/orders", response_model=GetOrderSchema, status_code=status.HTTP_201_CREATED
)
def place_order(
    order_details: PlaceOrderSchema, user_claims: UserClaims = Depends(validate_access)
):
    with session_maker() as session:
        order = OrderModel(
            user=user_claims.sub,
            product=order_details.product,
            quantity=order_details.quantity,
        )
        session.add(order)
        session.commit()
        return {
            "id": order.id,
            "product": order.product,
            "quantity": order.quantity,
        }


@server.get("/orders/{order_id}")
def get_order_details(
    order_id: uuid.UUID, user_claims: UserClaims = Depends(validate_access)
):
    with session_maker() as session:
        order = session.scalar(
            select(OrderModel).where(
                OrderModel.id == order_id, OrderModel.user == user_claims.sub
            )
        )
        if order is None:
            raise HTTPException(
                status_code=404, detail=f"Order with ID {order_id} not found."
            )
    return {
        "id": order.id,
        "product": order.product,
        "quantity": order.quantity,
    }
