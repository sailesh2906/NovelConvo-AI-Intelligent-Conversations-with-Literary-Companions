import requests
import json

# The URL of the Flask app
# url = 'http://34.168.237.117:5000/chat'
url = 'http://localhost:5000/chat'

# Initialize chat_history_ids to None for the first request
chat_history_ids = None

# Let's chat for 5 lines
for step in range(5):
    # User input
    user_input = input(">> User: ")

    # Prepare the data payload
    data = {
        'prompt': user_input,
        'chat_history_ids': chat_history_ids
    }

    # Make the POST request
    response = requests.post(url, json=data)

    # Extract the response
    if response.status_code == 200:
        response_data = response.json()
        print("DialoGPT:", response_data['output'])
        chat_history_ids = response_data['chat_history_ids']
    else:
        print("Error:", response.status_code, response.text)
        break