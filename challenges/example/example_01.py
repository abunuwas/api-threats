import enum
import uuid
from typing import Optional

import requests
from fastapi import HTTPException, Depends, FastAPI
from jinja2 import Template
from pydantic import BaseModel, ConfigDict
from pydantic_core import Url
from sqlalchemy import select, text
from starlette import status
from starlette.responses import HTMLResponse

from auth import UserClaims, authorize_access
from models import session_maker, OrderModel, ProductModel

server = FastAPI(
    title="API Threats Example 01",
    description="API Threats Example 01",
)


class ProductSchema(BaseModel):
    id: uuid.UUID
    name: str
    price: float
    stock: int


class ListProducts(BaseModel):
    products: list[ProductSchema]


class PlaceOrderSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    product_id: uuid.UUID
    amount: int


class OrderStatusEnum(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    delivered = "delivered"


class GetOrderSchema(PlaceOrderSchema):
    id: uuid.UUID
    user_id: str
    status: OrderStatusEnum


class ListOrders(BaseModel):
    orders: list[GetOrderSchema]


class OrderByEnum(enum.Enum):
    name = "name"
    price = "price"


@server.get("/products", response_model=ListProducts)
def list_products(
    page: Optional[int] = 1,
    per_page: Optional[int] = 10,
    order_by: Optional[str] = "price",
):
    # pagination attack: request 1M
    # schema enumeration: stock, discount
    with session_maker() as session:
        order_by = getattr(ProductModel, order_by)
        query = (
            select(ProductModel)
            .limit(per_page)
            .offset(page - 1 if page == 1 else (page - 1) * per_page)
            .order_by(order_by)
        )
        return {"products": list(session.scalars(query))}


@server.get("/orders", response_model=ListOrders)
def list_orders(
    user_claims: UserClaims = Depends(authorize_access), status: Optional[str] = None
):
    # BOLA
    # injection param: ' OR 1=1--
    with session_maker() as session:
        query = f"select * from 'order' " f"where user_id = '{user_claims.sub}' "
        if status is not None:
            query += f"and status = '{status}'"
        query += ";"

        orders = session.execute(text(query))
        return {"orders": orders}


@server.post(
    "/orders",
    status_code=status.HTTP_201_CREATED,
    response_model=GetOrderSchema,
)
def place_order(
    order_details: PlaceOrderSchema, user_claims: UserClaims = Depends(authorize_access)
):
    with session_maker() as session:
        order = OrderModel(
            product_id=order_details.product_id,
            amount=order_details.amount,
            user_id=user_claims.sub,
            status=OrderStatusEnum.pending.value,
        )
        session.add(order)
        session.commit()
        session.refresh(order)
        return order


@server.get("/orders/{order_id}", response_model=GetOrderSchema)
def get_order_details(order_id: uuid.UUID):
    # anyone can see each other's orders
    with session_maker() as session:
        order = session.scalar(select(OrderModel).where(OrderModel.id == order_id))
        if order is not None:
            return order
        raise HTTPException(
            status_code=404, detail=f"Order with ID {order_id} not found"
        )


@server.put("/orders/{order_id}", response_model=GetOrderSchema)
def update_order_details(order_id: uuid.UUID, order_details: PlaceOrderSchema):
    # mass assignment
    with session_maker() as session:
        order = session.scalar(select(OrderModel).where(OrderModel.id == order_id))

        if order is not None:
            for key, value in order_details:
                setattr(order, key, value)
            session.commit()
            session.refresh(order)
            return order

        raise HTTPException(
            status_code=404, detail=f"Order with ID {order_id} not found"
        )


@server.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: uuid.UUID):
    with session_maker() as session:
        order = session.scalar(select(OrderModel).where(OrderModel.id == order_id))
        if order is None:
            raise HTTPException(
                status_code=404, detail=f"Order with ID {order_id} not found"
            )
        session.delete(order)
        session.commit()


@server.get("/fetch-external-data")
def fetch_external_data(url: Url):
    # ssrf
    return requests.get(url).content


@server.get("/fetch-external-data-safe")
def fetch_external_data_safe(url: Url):
    # ssrf
    if "localhost" in str(url):
        raise HTTPException(422, "Requests to localhost not allowed")
    return requests.get(url).content


@server.get("/companies", response_class=HTMLResponse)
def companies():
    companies = requests.get("http://localhost:8000/example_01/uk-companies").json()
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Company List</title>
        <style>
            body { font-family: Arial, sans-serif; }
            table { width: 50%; margin: auto; border-collapse: collapse; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1 style="text-align:center;">Company List</h1>
        <table>
            <tr>
                <th>Company Name</th>
                <th>Director</th>
            </tr>
    """

    for company in companies["companies"]:
        html_content += f"""
            <tr>
                <td>{company['name']}</td>
                <td>{company['director']}</td>
            </tr>
        """

    html_content += """
        </table>
    </body>
    </html>
    """

    return html_content


@server.get("/companies-safe", response_class=HTMLResponse)
def companies_safe():
    response = requests.get("http://localhost:8000/example_01/uk-companies")
    response.raise_for_status()  # Ensure we catch any errors from the request
    companies = response.json()

    template = Template(
        """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Company List</title>
        <style>
            body { font-family: Arial, sans-serif; }
            table { width: 50%; margin: auto; border-collapse: collapse; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1 style="text-align:center;">Company List</h1>
        <table>
            <tr>
                <th>Company Name</th>
                <th>Director</th>
            </tr>
            {% for company in companies %}
            <tr>
                <td>{{ company.name|e }}</td>
                <td>{{ company.director|e }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    )

    html_content = template.render(companies=companies["companies"])

    return HTMLResponse(content=html_content)


@server.get("/example_01/secrets", include_in_schema=False)
def leak_secrets():
    return "super secret!"


@server.get("/example_01/uk-companies", include_in_schema=False)
def list_uk_companies():
    return {
        "companies": [
            {
                "name": "<script>alert('hello,world!')</script>microapis.io",
                "director": "Jose Haro Peralta",
            },
            {
                "name": "<SCRIPT SRC=HTTPS://MJT.XSS.HT></script> LTD",
                "director": "Michael Tandy",
            },
        ]
    }
