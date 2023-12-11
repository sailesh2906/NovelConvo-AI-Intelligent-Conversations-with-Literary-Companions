from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import chitchat_dataset as ccc
import yaml
import os
import json

# Initialize the chatbot
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
trainer = ListTrainer(bot)

# Specify the path to the corpus
corpus_directory = os.path.join(os.getcwd(), 'data/chatterbot_corpus/data/english')  # Update this path based on your environment
corpus_files = [os.path.join(corpus_directory, f) for f in os.listdir(corpus_directory) if f.endswith('.yml')]

# Train the bot
for file in corpus_files:
    with open(file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)  # Use safe_load to read YAML file
        for conversation in data['conversations']:
            trainer.train(conversation)




dataset = ccc.Dataset()
data_set = []

# Dataset is a subclass of dict()
for _ , convo in dataset.items():
    for conversation in convo['messages']:
        for chat in conversation:
            data_set.append(chat['text'])


print('chit_chatdataset')
trainer = ListTrainer(bot)
trainer.train(data_set)


print('Training with nfl6 data')
qa_data = json.loads(open('data/nfL6.json','r').read())

qa = []
for row in qa_data:
    qa.append(row['question'])
    qa.append(row['answer'])

trainer.train(qa)
