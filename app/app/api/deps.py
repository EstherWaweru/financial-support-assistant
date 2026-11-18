import enum
from collections.abc import Generator
from types import SimpleNamespace

from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def get_db() -> Generator:
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


class OrderDirection(enum.Enum):
    DESC = "desc"
    ASC = "asc"


class Order(SimpleNamespace):
    attribute: str
    order_direction: OrderDirection
