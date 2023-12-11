from chatterbot import ChatBot

from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    # Extract data from request
    data = request.json
    user_input = data['prompt']
    bot = ChatBot(
        'Query Alchemist',
        storage_adapter='chatterbot.storage.SQLStorageAdapter',
        database_uri='sqlite:///conversation_database.db',
        logic_adapters=[
            {
                'import_path': 'chatterbot.logic.BestMatch',
                'default_response': 'I am sorry, but I do not understand.',
                'maximum_similarity_threshold': 0.90
            }
        ]
    )

    redirect = False
    response = bot.get_response(user_input)
    if response.text == 'I am sorry, but I do not understand.':
        redirect = True
    result = {'output':response.text, 'redirect': redirect}
    
    # Return the result
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
