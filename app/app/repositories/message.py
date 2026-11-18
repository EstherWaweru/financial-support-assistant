from app.repositories.base import CRUDBase
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageUpdate


class CRUDMessage(CRUDBase[Message, MessageCreate, MessageUpdate]):
    pass


message = CRUDMessage(Message)
