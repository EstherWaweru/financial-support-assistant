# AI-Powered Financial Support Assistant

An AI-powered financial customer support application built with Python, FastAPI, PostgreSQL, and OpenRouter.

The application helps customers resolve payment related queries through a conversational interface. It uses an LLM to understand customer questions and backend tools to retrieve accurate, transaction specific information.

## Features

- **AI-powered conversations:** Uses OpenRouter to generate natural-language responses.
- **Tool calling:** Allows the LLM to request approved backend functions.
- **Transaction lookups:** Retrieves transaction information from the backend.
- **Conversation management:** Creates conversations, stores messages, and retrieves conversation history.
- **Context retention:** Maintains conversation history to support follow-up questions.
- **Customer data isolation:** Ensures customers can only access their own conversations and transactions.
- **Internal tool execution:** Persists tool calls and results without exposing them in customer-facing conversation history.
- **JWT authentication:** Planned implementation for securing customer access.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Database migrations | Alembic |
| AI provider | OpenRouter |
| API communication | REST,   Requests |
| Data validation | Pydantic |
| Containerization | Docker, Docker Compose |
| Dependency management | Poetry |
| Authentication | JWT (in progress) |
| Testing | Pytest |

## Architecture

The application follows a layered architecture that separates API handling, business logic, data persistence, and LLM integration.



### Request flow

1. A customer submits a message through the API.
2. The application retrieves the relevant conversation history.
3. The LLM receives the conversation context and available tool definitions.
4. If transaction specific information is required, the LLM requests an approved backend tool.
5. The backend validates the tool arguments and executes the function.
6. Tool results are returned to the LLM.
7. The LLM generates a customer facing response.
8. The application persists the messages and returns the response.

**Important architectural principle:** The LLM does not directly access the database or determine transaction facts. The backend remains the source of truth for financial information.

## Getting Started

### Prerequisites

- Python 3.12+
- Poetry
- Docker and Docker Compose
- OpenRouter API key

### 1. Clone the repository

```bash
git clone <repository-url>
cd financial-support-assistant
```

### 2. Install dependencies

```bash
poetry install
```

### 3. Configure environment variables

Create a `.env` file in the project root.

```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=your_model_id

POSTGRES_PASSWORD=your_database_password
DATABASE_URL=postgresql+psycopg://app_user:your_database_password@db:5432/financial_support

JWT_SECRET_KEY=your_generated_secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Generate a secure JWT secret using:

```bash
openssl rand -hex 32
```

### 4. Start the application

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000
```

### 5. Run database migrations

```bash
docker compose exec api alembic upgrade head
```

### 6. Access API documentation

FastAPI provides interactive API documentation through Swagger UI:

```text
http://localhost:8000/docs
```

## API Endpoints

### Conversations

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/conversations/` | Create a new conversation |
| GET | `/api/v1/conversations/{conversation_id}` | Retrieve conversation history |
| POST | `/api/v1/conversations/{conversation_id}/messages` | Send a message to an existing conversation |

### Example: Create a conversation

**Request**

```http
POST /api/v1/conversations/
Content-Type: application/json
```

```json
{
  "message": "Where is my transfer with transaction ID 12336236?"
}
```

**Example response**

```json
{
  "conversation_id": "your-conversation-id",
  "response": "Your transfer is currently processing."
}
```

### Example: Send a follow-up message

**Request**

```http
POST /api/v1/conversations/{conversation_id}/messages
Content-Type: application/json
```

```json
{
  "message": "What currency was the transfer in?"
}
```

The assistant uses the existing conversation history to understand the follow-up question.

## Security Considerations

The application is being developed with the following security principles:

- Backend-controlled access to financial data.
- Customer-level authorization for transactions and conversations.
- Validation of LLM-generated tool arguments.
- Allowlisted tool execution rather than dynamic function execution.
- Separation between internal tool messages and customer-visible responses.
- Secure password hashing and JWT authentication (in progress).
- Sensitive credentials stored in environment variables.

Customer identity must be obtained from authenticated backend context, never trusted from an LLM-generated tool argument or an arbitrary client-supplied customer ID.

## Development Roadmap

- [x] OpenRouter REST API integration
- [x] FastAPI application setup
- [x] Transaction lookup backend function
- [x] LLM function/tool calling
- [x] Tool argument validation and execution
- [x] PostgreSQL integration
- [x] SQLAlchemy models
- [x] Alembic database migrations
- [x] Conversation creation and retrieval
- [x] Message persistence
- [x] Conversation history and context retention
- [x] Customer-visible message filtering
- [x] Conversation timestamp updates
- [ ] JWT authentication and customer registration
- [ ] API-level integration tests
- [ ] Improved error handling and reliability
- [ ] Knowledge base and Retrieval-Augmented Generation (RAG)
- [ ] AI response evaluation and security testing
- [ ] Production deployment and monitoring

## Running Tests

Tests are written using Pytest.

Run the test suite with:

```bash
poetry run pytest
```

## Project Goals

This project is intended to demonstrate practical AI integration engineering, including:

- Integrating LLMs into backend applications.
- Designing reliable tool calling workflows.
- Building secure financial API integrations.
- Managing conversation state and context.
- Implementing data validation and authorization.
- Developing maintainable, testable backend services.
- Applying production oriented software engineering practices.
