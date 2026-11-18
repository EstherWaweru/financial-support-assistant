from app.repositories.base import CRUDBase
from app.models.conversation import Conversation
from app.schemas.conversation import ConversationCreate, ConversationUpdate


class CRUDConversation(CRUDBase[Conversation, ConversationCreate, ConversationUpdate]):
    pass


conversation = CRUDConversation(Conversation)
