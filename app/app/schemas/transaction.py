from pydantic import ConfigDict, BaseModel


class TransactionLookupArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transaction_id: str
