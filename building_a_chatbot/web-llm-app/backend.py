from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from tinydb import Query, TinyDB  # TinyDB stores chat history in a local JSON file.
from datetime import datetime, UTC
import uuid

load_dotenv()
llm = OpenAI()
INITIAL_ASSISTANT_MESSAGE = 'How can I help you today?'

# Create the FastAPI application object.
app = FastAPI()

# Serve files from ./static at the /static URL path.
app.mount('/static', StaticFiles(directory='static'), name='static')

# Open or create the TinyDB JSON file.
db = TinyDB('chat_db.json')
# Use a dedicated "conversations" table for chat sessions.
conversations = db.table('conversations')


# Request model for POST /chat.
class ChatRequest(BaseModel):
    session_id: str
    user_input: str


# Response model for POST /chat.
class ChatResponse(BaseModel):
    reply: str  # Assistant reply text sent back to the browser.


# Response model for POST /new-session.
class NewSessionResponse(BaseModel):
    session_id: str  # Fresh UUID session id.


# Response model for GET /history/{session_id}.
class HistoryResponse(BaseModel):
    messages: list[dict[str, str]]  # Full message history for a single session.


@app.get('/')
def read_index():
    return FileResponse('static/index.html')


# Main chat endpoint called by the frontend.
@app.post('/chat', response_model=ChatResponse)
def chat(payload: ChatRequest):
    # Load existing conversation for this session, if it exists:
    conversation = conversations.get(Query().session_id == payload.session_id)
    # Start from stored messages or an empty list for new sessions:
    messages = conversation['messages'] if conversation else []

    # Match chatbot.py behavior: history begins with assistant's opening message.
    if not messages:
        messages.append({'role': 'assistant', 'content': INITIAL_ASSISTANT_MESSAGE})

    # Add the latest user message to history before calling the model:
    messages.append({'role': 'user', 'content': payload.user_input})

    # Convert array of messages into single string for the LLM prompt:
    history_lines = []
    for message in messages:
        if message['role'] == 'user':
            history_lines.append(f"User: {message['content']}")
        else:
            history_lines.append(f"Assistant: {message['content']}")

    history = '\n'.join(history_lines)

    # Generate the LLM response from OpenAI:
    response = llm.responses.create(
        model='gpt-4.1-mini',
        temperature=0,
        input=history,
    )

    reply = response.output_text

    # Persist assistant reply in the same conversation history:
    messages.append({'role': 'assistant', 'content': reply})

    # Add the session record with latest messages + timestamp to DB:
    conversations.upsert(
        {
            'session_id': payload.session_id,
            'messages': messages,
            'updated_at': datetime.now(UTC).isoformat(),
        },
        Query().session_id == payload.session_id,
    )

    # Return the assistant reply to the frontend.
    return ChatResponse(reply=reply)


# Create and return a new UUID for starting a fresh chat session.
@app.post('/new-session', response_model=NewSessionResponse)
def new_session():
    return NewSessionResponse(session_id=str(uuid.uuid4()))


# Return all messages for a given session id.
@app.get('/history/{session_id}', response_model=HistoryResponse)
def history(session_id: str):
    # Look up the conversation record.
    conversation = conversations.get(Query().session_id == session_id)
    # If no record exists, return an empty message list.
    messages = conversation['messages'] if conversation else []
    return HistoryResponse(messages=messages)
