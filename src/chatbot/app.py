from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/chat', methods=['POST'])
def chat():
    # Extract data from request
    data = request.json

    input_prompt = data['prompt']
    chat_history_ids = data['chat_history_ids']

    if chat_history_ids is not None:
        chat_history_ids = torch.tensor(chat_history_ids)

    new_user_input_ids = tokenizer.encode(input_prompt + tokenizer.eos_token, return_tensors='pt')

    if chat_history_ids is not None:
        bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1)
    else:
        bot_input_ids = new_user_input_ids

    chat_history_ids = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)

    output = tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)

    # Call your Python function here with the data
    result = {'output': output, 'chat_history_ids': chat_history_ids.tolist()}

    # Return the result
    return jsonify(result)


if __name__ == '__main__':
    tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium", padding_side='left')
    model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

    app.run(debug=True, host='0.0.0.0', port=5000)
