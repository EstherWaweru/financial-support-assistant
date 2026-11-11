TRANSACTION_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_transaction_status",
            "description": (
                "Retrieve the status of a customer's "
                "transaction using its transaction ID."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "transaction_id": {
                        "type": "string",
                        "description": "The transaction ID to look up.",
                    }
                },
                "required": ["transaction_id"],
                "additionalProperties": False,
            },
        },
    }
]
