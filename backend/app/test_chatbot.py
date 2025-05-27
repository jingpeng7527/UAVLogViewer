import requests
import json
from datetime import datetime, timedelta

# Sample flight data that simulates a real MAVLink log
SAMPLE_FLIGHT_DATA = {
    "GPS": [
        {"timestamp": "2024-03-20T10:00:00", "alt": 100, "fix_type": 3},
        {"timestamp": "2024-03-20T10:01:00", "alt": 150, "fix_type": 3},
        {"timestamp": "2024-03-20T10:02:00", "alt": 200, "fix_type": 3},
        {"timestamp": "2024-03-20T10:03:00", "alt": 250, "fix_type": 2},  # GPS signal degraded
        {"timestamp": "2024-03-20T10:04:00", "alt": 300, "fix_type": 3},
        {"timestamp": "2024-03-20T10:05:00", "alt": 250, "fix_type": 3},
    ],
    "BAT": [
        {"timestamp": "2024-03-20T10:00:00", "voltage": 12.6, "temperature": 25},
        {"timestamp": "2024-03-20T10:01:00", "voltage": 12.4, "temperature": 28},
        {"timestamp": "2024-03-20T10:02:00", "voltage": 12.2, "temperature": 32},
        {"timestamp": "2024-03-20T10:03:00", "voltage": 12.0, "temperature": 35},
        {"timestamp": "2024-03-20T10:04:00", "voltage": 11.8, "temperature": 38},
        {"timestamp": "2024-03-20T10:05:00", "voltage": 11.6, "temperature": 40},
    ],
    "RCIN": [
        {"timestamp": "2024-03-20T10:00:00", "status": 1},
        {"timestamp": "2024-03-20T10:01:00", "status": 1},
        {"timestamp": "2024-03-20T10:02:00", "status": 0},  # RC signal lost
        {"timestamp": "2024-03-20T10:03:00", "status": 0},  # RC signal lost
        {"timestamp": "2024-03-20T10:04:00", "status": 1},
        {"timestamp": "2024-03-20T10:05:00", "status": 1},
    ]
}

def test_chatbot():
    base_url = "http://localhost:8000"
    conversation_history = []

    # Test questions
    test_questions = [
        "What was the highest altitude reached during the flight?",
        "When did the GPS signal first get lost?",
        "What was the maximum battery temperature?",
        "How long was the total flight time?",
        "List all critical errors that happened mid-flight.",
        "When was the first instance of RC signal loss?"
    ]

    print("Starting chatbot tests...\n")

    for question in test_questions:
        print(f"\nQuestion: {question}")
        
        # Prepare the request
        payload = {
            "messages": [
                {"role": "user", "content": question}
            ],
            "flight_data": SAMPLE_FLIGHT_DATA
        }

        try:
            # Send the request
            response = requests.post(f"{base_url}/api/chat", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                print(f"Response: {result['response']}")
                print(f"Timestamp: {result['timestamp']}")
            else:
                print(f"Error: {response.status_code}")
                print(f"Details: {response.text}")

        except Exception as e:
            print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    test_chatbot() 