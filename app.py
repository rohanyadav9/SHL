from fastapi import FastAPI
from pydantic import BaseModel
from convo import ConversationManager

app = FastAPI(
    title="SHL Assessment Recommendation API",
    version="1.0.0"
)

manager = ConversationManager()


###########################################################
# Request Model
###########################################################

class ChatRequest(BaseModel):

    session_id: str | None = None

    message: str


###########################################################
# Health
###########################################################

@app.get("/health")
def health():

    return {

        "status": "healthy"

    }


###########################################################
# Chat
###########################################################

@app.post("/chat")
def chat(request: ChatRequest):

    session = request.session_id

    if session is None:

        session = manager.create_session()

    result = manager.chat(

        session,

        request.message

    )

    result["session_id"] = session

    return result