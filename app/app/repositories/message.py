from app.repositories.base import CRUDBase
from app.models.message import Message
from app.schemas.message import MessageCreate


class CRUDMessage(CRUDBase[Message, MessageCreate]):
    pass


message = CRUDMessage(Message)
