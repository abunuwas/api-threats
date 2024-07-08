import uuid

from sqlalchemy import create_engine, select, Uuid, ForeignKey
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)


class ProductModel(Base):
    __tablename__ = "product"

    name: Mapped[str]
    price: Mapped[float]
    stock: Mapped[int]
    discount: Mapped[float]
    is_exclusive: Mapped[bool]


class OrderModel(Base):
    __tablename__ = "order"

    user_id: Mapped[str]
    product_id: Mapped[Uuid] = mapped_column(ForeignKey("product.id"))
    amount: Mapped[int]
    status: Mapped[str]


products = [
    {
        "name": "coffee",
        "price": 10,
        "stock": 1000,
        "discount": 50,
        "is_exclusive": True,
    },
    {"name": "tea", "price": 1, "stock": 10, "discount": 10, "is_exclusive": False},
]

orders = [
    {
        "user_id": str(uuid.uuid4()),
        "product_id": "",
        "amount": 1,
        "status": "delivered",
    },
    {
        "user_id": str(uuid.uuid4()),
        "product_id": "",
        "amount": 1,
        "status": "delivered",
    },
]


Base.metadata.create_all(create_engine("sqlite:///example.db"))


session_maker = sessionmaker(bind=create_engine("sqlite:///example.db"))

with session_maker() as session:
    if not list(session.scalars(select(ProductModel))):
        pp = []
        for product in products:
            pp.append(ProductModel(**product))
        session.add_all(pp)
        session.commit()

        oo = []
        for order in orders:
            order["product_id"] = pp[0].id
            oo.append(OrderModel(**order))
        session.add_all(oo)
        session.commit()
