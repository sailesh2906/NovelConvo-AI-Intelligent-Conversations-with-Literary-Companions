from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline

import nltk
import string
import pandas as pd
import numpy as np
import requests

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

app = Flask(__name__)
CORS(app)

CHITCHAT_URL = 'http://34.168.123.224:5000/chat'
RAG_URL = 'http://34.125.217.36:5000/rag'

CHAT_VAL = "Initialing or Continuing Conversation"
FAREWELL_VAL = "Concluding Conversation"
NOVELS_VAL = "Seeking Information on Novels"

BOOKS_MAP = {
    0: "The Adventures of Sherlock Holmes",
    1: "Romeo and Juliet",
    2: "The Iliad",
    3: "Gulliver's Travels",
    4: "Moby Dick",
    5: "Hervey Willetts",
    6: "Babbitt",
    7: "Dracula",
    8: "Adventures of Huckleberry Finn",
    9: "The Alchemist",
}


def pre_processing(paragraph):
    text = paragraph.replace("'", "")
    text = text.replace('“', "")
    text = text.replace('”', "")
    text = text.replace('"', "")
    text = text.replace('_', "")
    text = text.replace('—', "")
    text = text.replace('-', " ")
    text = text.replace('\n', "")
    stop = set(nltk.corpus.stopwords.words('english') + list(string.punctuation))
    filtered_words = text.lower().split()
    filtered_words = [word for word in filtered_words if word not in stop]
    lemmatizer = nltk.stem.WordNetLemmatizer()
    lemmatized_words = [lemmatizer.lemmatize(word) for word in filtered_words]
    para = ' '.join(lemmatized_words)

    return para


def search_results(books, query):
    title_str = f'title:"{books[0]}"'
    for i in range(1, len(books)):
        title_str = title_str + ' OR ' + f'title:"{books[i]}"'
    title_str = '(' + title_str + ')'
    query_list = query.split()
    query_str = f'paragraph:"{query_list[0]}"'
    for i in range(1, len(query_list)):
        query_str = query_str + ' OR ' + f'paragraph:"{query_list[i]}"'
    query_str = '(' + query_str + ')'
    solr_url = f'http://34.125.172.59:8983/solr/IRF23P3/select?q={title_str} AND {query_str}&wt=json&rows=5'

    print(solr_url)
    try:
        response = requests.get(solr_url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()['response']['docs']
        if data:
            results_df = pd.DataFrame(data)
            results_df.drop(columns=['id', '_version_'], inplace=True)
            return results_df
        else:
            print("No results found")
            return pd.DataFrame()
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()


def classify(sequence_to_classify, candidate_labels, multi_label=None):
    result = classifier(sequence_to_classify, candidate_labels, multi_label=multi_label)

    if not multi_label:
        labels = result['labels']
        scores = result['scores']
        print(labels)
        print(scores)
        return labels[np.argmax(scores)]
    else:
        return []


@app.route('/chat', methods=['POST'])
def chat():
    # Extract data from request
    data = request.json
    print("Came here")

    input_prompt = data['prompt']
    books = data['books']
    prev_msgs = data['prev_msgs']
    print(books)

    classifier_output = classify(
        input_prompt,
        [CHAT_VAL, NOVELS_VAL, FAREWELL_VAL]
    )

    print(classifier_output)

    if classifier_output != NOVELS_VAL:
        response = requests.post(CHITCHAT_URL, json={
            'prompt': input_prompt,
        })
        cc_data = response.json()

        if not cc_data['redirect']:
            return jsonify({
                'output': cc_data['output'],
                'farewell': classifier_output == FAREWELL_VAL,
                'chit_chat': True
            })

    book_titles = []
    if not books:
        topic_classifier_output = classify(
            input_prompt,
            list(BOOKS_MAP.values())
        )
        print(topic_classifier_output)
        book_titles = [topic_classifier_output]
    else:
        book_titles = [BOOKS_MAP[book] for book in books]

    preprocessed_input = pre_processing(input_prompt)

    doc_df = search_results(book_titles, preprocessed_input)
    print(doc_df)

    doc_string = ''

    # for msg in prev_msgs:
    #     doc_string += (msg + ' /n ')

    if books and doc_df.empty:
        return jsonify({
            'output': "No results found!! Try changing filters",
            'farewell': False,
            'chit_chat': False
        })

    if not doc_df.empty:
        for i in range(min(5, doc_df.shape[0])):
            doc_string += (doc_df.paragraph[i] + ' /n ')

    response = requests.post(RAG_URL, json={
        'query': input_prompt,
        'docs': doc_string
    })

    rag_data = response.json()

    return jsonify({
        'output': rag_data['answer'],
        'farewell': False,
        'chit_chat': False
    })


if __name__ == '__main__':
    classifier = pipeline("zero-shot-classification", model="MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli")
    # classifier = pipeline("zero-shot-classification", model="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli")
    app.run(debug=True, host='0.0.0.0', port=5000)
