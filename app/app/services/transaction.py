# TODO: Replace the mock data by actual transaction data

TRANSACTIONS = {
    "12336236": {
        "transaction_id": "12336236",
        "customer_id": "customer_001",
        "amount": 1500,
        "currency": "KES",
        "status": "processing",
        "description": "Bank transfer",
    },
    "98765432": {
        "transaction_id": "98765432",
        "customer_id": "customer_002",
        "amount": 2500,
        "currency": "KES",
        "status": "completed",
        "description": "Bank transfer",
    },
}


def get_transaction_status(
    transaction_id: str,
    customer_id: str,
) -> dict | None:

    transaction = TRANSACTIONS.get(transaction_id)

    if not transaction:
        return None

    if transaction["customer_id"] != customer_id:
        return None

    return {
        "transaction_id": transaction["transaction_id"],
        "amount": transaction["amount"],
        "currency": transaction["currency"],
        "status": transaction["status"],
        "description": transaction["description"],
    }
