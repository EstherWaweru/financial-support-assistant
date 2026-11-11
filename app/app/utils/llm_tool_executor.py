import json

from pydantic import ValidationError

from app.services.transaction import (
    get_transaction_status,
)

from app.schemas.transaction import TransactionLookupArgs


def execute_tool_call(
    tool_call: dict,
    customer_id: str,
) -> dict:
    function = tool_call["function"]
    function_name = function["name"]

    try:
        arguments = json.loads(function["arguments"])

        if function_name == "get_transaction_status":
            validated_args = TransactionLookupArgs.model_validate(arguments)

            transaction = get_transaction_status(
                transaction_id=validated_args.transaction_id,
                customer_id=customer_id,
            )

            if transaction is None:
                return {
                    "status": "not_found",
                    "message": "Transaction not found.",
                }

            return {
                "status": "success",
                "transaction": transaction,
            }

        return {
            "status": "error",
            "message": "Unsupported tool.",
        }

    except (json.JSONDecodeError, ValidationError):
        return {
            "status": "error",
            "message": "Invalid tool arguments.",
        }
