from flask import Flask, request, jsonify
from flask_cors import CORS

import nltk
import string
import pandas as pd
import requests

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

app = Flask(__name__)
CORS(app)

CLASSIFIER_URL = 'http://34.168.52.156:5000/classify'
CHITCHAT_URL = 'http://34.168.123.224:5000/chat'
RAG_URL = 'http://34.125.217.36:5000/rag'

CHAT_VAL = "chat"
FAREWELL_VAL = "bye"
NOVELS_VAL = "novels"

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
    filtered_words = [i.lower().strip() for i in nltk.word_tokenize(text) if i not in stop]
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
        results_df = pd.DataFrame(data)
        if not results_df.empty:
            results_df.drop(columns=['id', '_version_'], inplace=True)
            return results_df
        else:
            print("No results found")
            return False
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return False


@app.route('/chat', methods=['POST'])
def chat():
    # Extract data from request
    data = request.json
    print("Came here")

    input_prompt = data['prompt']
    books = data['books']
    prev_msgs = data['prev_msgs']
    print(books)
    response = requests.post(CLASSIFIER_URL, json={
        'sequence_to_classify': input_prompt,
        'candidate_labels': [CHAT_VAL, NOVELS_VAL, FAREWELL_VAL]
    })

    classifier_data = response.json()

    classifier_output = classifier_data['label']
    print(classifier_output)

    if classifier_output != NOVELS_VAL:
        # response = requests.post(CLASSIFIER_URL, json={
        #     'sequence_to_classify': input_prompt,
        #     'candidate_labels': ['farewell', 'not farewell']
        # })
        # farewell_data = response.json()
        # farewell_output = farewell_data['label']
        #
        # print(farewell_output)

        response = requests.post(CHITCHAT_URL, json={
            'prompt': input_prompt,
        })
        cc_data = response.json()
        return jsonify({
            'output': cc_data['output'],
            'farewell': classifier_output == FAREWELL_VAL,
            'chit_chat': True
        })
    else:
        if not books:
            print(list(BOOKS_MAP.values()))
            response = requests.post(CLASSIFIER_URL, json={
                'sequence_to_classify': input_prompt,
                'candidate_labels': list(BOOKS_MAP.values())
            })
            topic_classifier_data = response.json()
            topic_classifier_output = topic_classifier_data['label']
            print(topic_classifier_output)
            books = [topic_classifier_output]

        preprocessed_input = pre_processing(input_prompt)

        res = search_results([BOOKS_MAP[0]], preprocessed_input)
        print("results here")
        print(res)
        if not res:
            jsonify({
                'output': "No results found!! Try again",
                'farewell': False,
                'chit_chat': False
            })

        doc_string = ''

        for msg in prev_msgs:
            doc_string += (msg + ' /n ')

        for i in range(5):
            doc_string += (res.paragraph[i] + ' /n ')

        response = requests.post(RAG_URL, json={
            'query': input_prompt,
            'docs': doc_string
        })
        print(response.status_code)
        rag_data = response.json()
        return jsonify({
            'output': rag_data['answer'],
            'farewell': False,
            'chit_chat': False
        })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
