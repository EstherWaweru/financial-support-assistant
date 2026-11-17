from app.repositories.base import CRUDBase
from app.models.conversation import Conversation
from app.schemas.conversation import ConversationCreate


class CRUDConversation(CRUDBase[Conversation, ConversationCreate]):
    pass


conversation = CRUDConversation(Conversation)
