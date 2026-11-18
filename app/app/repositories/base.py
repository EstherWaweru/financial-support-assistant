from sqlalchemy.sql.elements import or_, and_
from datetime import timezone
from app.api.deps import OrderDirection, Order
from app.repositories.filter import Filter
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union, Tuple
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query
from app.db.base import Base
from datetime import datetime

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        db_obj = db.get(self.model, id)  # type: ignore
        return db_obj  # type: ignore

    def get_by(self, **kw: Any) -> Optional[ModelType]:
        result = self.get_multi(**kw)
        if result:
            return result[0]
        else:
            return None

    def get_multi(
        self,
        db: Session,
        base_query: Query = None,
        Or: bool = False,
        filter: Filter = Filter(),
        order_by: Optional[Order] = None,
        **kw: Any,
    ) -> List[ModelType]:

        if not isinstance(base_query, Query):
            base_query = db.query(self.model)
        query = self.apply_filter(base_query=base_query, filter=filter)

        direct_filter: List[Any] = []
        # for generic direct queries
        for key, value in kw.items():
            direct_filter.append(getattr(self.model, key) == value)

        if direct_filter and Or:
            query = query.filter(or_(*direct_filter))
        elif direct_filter:
            query = query.filter(and_(*direct_filter))

        if order_by and hasattr(self.model, order_by.attribute):
            attribute = getattr(self.model, order_by.attribute)
            if order_by.order_direction == OrderDirection.DESC:
                query = query.order_by(attribute.desc())
            elif order_by.order_direction == OrderDirection.ASC:
                query = query.order_by(attribute.asc())

        return query.all()

    def get_or_create(
        self, db: Session, *, obj_in: CreateSchemaType, creator: Optional[str] = None
    ) -> Tuple[ModelType, bool]:
        obj_in_data = jsonable_encoder(obj_in.dict(exclude_unset=True))
        db_obj = db.query(self.model).filter_by(**obj_in_data).first()
        if db_obj:
            return db_obj, False
        else:
            db_obj = self.create(db=db, obj_in=obj_in)
            return db_obj, True

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.flush()
        db.refresh(db_obj)
        return db_obj

    def create_multi(
        self,
        db: Session,
        *,
        obj_in: List[CreateSchemaType],
    ) -> List[ModelType]:
        obj_list = []
        for obj in obj_in:
            obj_in_data = jsonable_encoder(obj)
            db_obj = self.model(**obj_in_data)
            obj_list.append(db_obj)

        db.add_all(obj_list)
        db.flush()

        for obj in obj_list:
            db.refresh(obj)

        return obj_list

    def flush(self, db: Session, *, db_obj: ModelType) -> ModelType:
        db.add(db_obj)
        db.flush()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        # TODO: change to expire
        db.refresh(db_obj)
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        date_last_modified = datetime.now(timezone.utc)
        if date_last_modified and hasattr(db_obj, "date_last_modified"):
            db_obj.date_last_modified = date_last_modified  # type: ignore
        db.add(db_obj)
        db.flush()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> Optional[ModelType]:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.flush()
        return obj

    def apply_filter(self, base_query: Query, filter: Filter) -> Query:
        for key, item in filter.filter_list.items():
            for command, value in item.items():
                if hasattr(self.model, key) and command is not None:
                    column = getattr(self.model, key)
                    base_query = command.apply_command(
                        value=value, column=column, query=base_query
                    )

        return base_query
