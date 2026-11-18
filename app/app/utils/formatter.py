from app.models import Message


def format_message(message: Message) -> dict:
    formatted = {
        "role": message.role,
    }

    if message.content is not None:
        formatted["content"] = message.content

    if message.tool_calls is not None:
        formatted["tool_calls"] = message.tool_calls

    if message.tool_call_id is not None:
        formatted["tool_call_id"] = message.tool_call_id

    return formatted


def format_messages(messages: list[Message]) -> list[dict]:
    return [format_message(message) for message in messages]
