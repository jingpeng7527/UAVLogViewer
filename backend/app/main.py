from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv
import groq
from datetime import datetime
import json
from collections import defaultdict

# Load environment variables
load_dotenv()

app = FastAPI(title="UAV Logger Chatbot")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq client
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set")

client = groq.Groq(api_key=api_key)

# Store conversation state
conversation_states = defaultdict(lambda: {
    "messages": [],
    "flightData": None,
    "clarificationNeeded": False,
    "pendingQuestion": None,
    "context": {}
})

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    flightData: Optional[dict] = None
    sessionId: str = "default"

class ChatResponse(BaseModel):
    response: str
    timestamp: str
    needsClarification: bool = False
    clarificationQuestion: Optional[str] = None

def get_system_prompt(flight_data: Optional[dict] = None) -> str:
    base_prompt = """You are an expert UAV flight data analyst. Your role is to:
1. Analyze flight data and provide insights
2. Ask clarifying questions when information is ambiguous
3. Maintain context throughout the conversation
4. Proactively identify potential issues or interesting patterns
5. Guide users to relevant information

When you need clarification, ask specific questions that will help you provide better analysis.
When you notice something interesting or concerning in the data, point it out proactively.
"""
    if flight_data:
        return f"{base_prompt}\nCurrent flight data context: {json.dumps(flight_data)}"
    return base_prompt

def analyze_message_for_clarification(message: str, flight_data: Optional[dict]) -> tuple[bool, Optional[str]]:
    """Analyze if clarification is needed and what question to ask."""
    # Example clarification triggers
    clarification_triggers = {
        "altitude": ["high", "low", "altitude", "height"],
        "speed": ["fast", "slow", "speed", "velocity"],
        "location": ["where", "location", "position", "coordinates"],
        "time": ["when", "time", "duration", "how long"]
    }
    
    # Check if message contains ambiguous terms
    for category, triggers in clarification_triggers.items():
        if any(trigger in message.lower() for trigger in triggers):
            if not flight_data or category not in flight_data:
                return True, f"Could you specify which {category} you're interested in?"
    
    return False, None

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        session_state = conversation_states[request.sessionId]
        
        # Update flight data if provided
        if request.flightData:
            session_state["flightData"] = request.flightData
        
        # Add new messages to conversation history
        session_state["messages"].extend([{"role": msg.role, "content": msg.content} for msg in request.messages])
        
        # Check if we need to ask for clarification
        needs_clarification, clarification_question = analyze_message_for_clarification(
            request.messages[-1].content if request.messages else "",
            session_state["flightData"]
        )
        
        if needs_clarification:
            session_state["clarificationNeeded"] = True
            session_state["pendingQuestion"] = clarification_question
            return ChatResponse(
                response="I need some clarification to provide a better analysis.",
                timestamp=datetime.utcnow().isoformat(),
                needsClarification=True,
                clarificationQuestion=clarification_question
            )

        # Prepare the conversation history with system message
        messages = [{"role": "system", "content": get_system_prompt(session_state["flightData"])}]
        messages.extend(session_state["messages"])

        # Get response from Groq
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
            )
            
            response = completion.choices[0].message.content
            
            # Add assistant's response to conversation history
            session_state["messages"].append({"role": "assistant", "content": response})
            
            # Check if the response indicates a need for clarification
            if "?" in response and any(phrase in response.lower() for phrase in ["could you", "can you", "would you", "please specify"]):
                session_state["clarificationNeeded"] = True
                session_state["pendingQuestion"] = response
                return ChatResponse(
                    response=response,
                    timestamp=datetime.utcnow().isoformat(),
                    needsClarification=True,
                    clarificationQuestion=response
                )

            return ChatResponse(
                response=response,
                timestamp=datetime.utcnow().isoformat(),
                needsClarification=False
            )

        except Exception as groq_error:
            error_message = str(groq_error)
            if hasattr(groq_error, 'response'):
                try:
                    error_details = json.loads(groq_error.response.text)
                    error_message = f"Groq API Error: {error_details}"
                except:
                    error_message = f"Groq API Error: {groq_error.response.text}"
            raise HTTPException(status_code=500, detail=error_message)

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 