# UAV Logger Chatbot Backend

This is the backend service for the UAV Logger Chatbot, providing intelligent analysis of MAVLink flight logs using Groq's LLM API.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the `app` directory with the following content:
```
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:8080,http://localhost:3000
```

4. Run the server:
```bash
cd app
uvicorn main:app --reload
```

## API Endpoints

### POST /api/chat
Send chat messages to the UAV analysis chatbot.

Request body:
```json
{
    "messages": [
        {
            "role": "user",
            "content": "What was the highest altitude reached during the flight?"
        }
    ],
    "flight_data": {
        // Optional flight data context
    }
}
```

### GET /api/health
Health check endpoint.

## Features

- Integration with Groq's Mixtral-8x7b model for intelligent flight data analysis
- MAVLink data processing and analysis
- Critical event detection (GPS loss, RC signal loss, battery warnings)
- Performance metrics calculation
- Flight summary generation

## Development

The backend is built with:
- FastAPI for the web framework
- Groq for LLM integration
- Pydantic for data validation
- NumPy for numerical computations 