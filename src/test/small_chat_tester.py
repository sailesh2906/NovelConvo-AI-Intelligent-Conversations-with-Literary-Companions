import requests
import json

# The URL of the Flask app
url = 'http://34.168.123.224:5000/chat'


# Let's chat for 5 lines
for step in range(5):
    # User input
    user_input = input(">> User: ")

    # Prepare the data payload
    data = {
        'prompt': user_input
    }

    # Make the POST request
    response = requests.post(url, json=data)

    # Extract the response
    if response.status_code == 200:
        response_data = response.json()
        print("Query Alchemist:", response_data['output'])
    else:
        print("Error:", response.status_code, response.text)
        break