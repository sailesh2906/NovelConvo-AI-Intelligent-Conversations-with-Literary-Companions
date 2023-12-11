from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline

import nltk
import string
import pandas as pd
import numpy as np
import requests
import sqlite3
from datetime import datetime
from collections import Counter

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


def service_down_error(chit_chat):
    return {
        'output': "Service Down!!",
        'farewell': True,
        'chit-chat': chit_chat
    }


def append_prev_messages(prompt, prev_msgs=None):
    return_prompt = prompt

    if not prev_msgs:
        return prompt

    for msg in prev_msgs:
        return_prompt += (msg + ' /n ')

    return return_prompt


def insert_conversation_in_db(data):
    conn = sqlite3.connect('metadata.sqlite')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO message_logs (timestamp, conversation_id, prompt, response, original_book_id, predicted_book_id, response_type, solar_documents_return_count) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', [data['timestamp'], data['conversation_id'], data['prompt'], data['response'], data['original_book_id'], data['predicted_book_id'], data['response_type'], data['solar_documents_return_count']])
    conn.commit()
    conn.close()


@app.route('/chat', methods=['POST'])
def chat():
    # Extract data from request
    data = request.json
    print("Came here")

    input_prompt = data['prompt']
    books = data['books']
    prev_msgs = data['prev_msgs']
    print(books)

    analytics_data = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
        'conversation_id': data['conversation_id'],
        'prompt': input_prompt,
        'response': '',
        'original_book_id': books[0] if books else None,
        'predicted_book_id': None,
        'response_type': '',
        'solar_documents_return_count': None
    }

    classifier_output = classify(
        input_prompt,
        [CHAT_VAL, NOVELS_VAL, FAREWELL_VAL]
    )

    print(classifier_output)

    if classifier_output != NOVELS_VAL:
        response = requests.post(CHITCHAT_URL, json={
            'prompt': input_prompt,
        })

        if response.status_code != 200:
            return jsonify(service_down_error(True))

        cc_data = response.json()
        if not cc_data['redirect']:
            analytics_data['response'] = cc_data['output']
            analytics_data['response_type'] = 'chat'
            insert_conversation_in_db(analytics_data)
            return jsonify({
                'output': cc_data['output'],
                'farewell': classifier_output == FAREWELL_VAL,
                'chit_chat': True
            })

    topic_classifier_output = classify(
        append_prev_messages(input_prompt, prev_msgs),
        list(BOOKS_MAP.values())
    )
    print(topic_classifier_output)

    predicted_book_id = [i for i in BOOKS_MAP if BOOKS_MAP[i] == topic_classifier_output][0]

    preprocessed_input = pre_processing(input_prompt)

    doc_dfs_map = {}
    if not books:
        book_titles = [topic_classifier_output]
        doc_df = search_results(book_titles, preprocessed_input)
        if not doc_df.empty:
            doc_dfs_map[predicted_book_id] = doc_df
    else:
        for book in books:
            doc_df = search_results([BOOKS_MAP[book]], preprocessed_input)
            if not doc_df.empty:
                doc_dfs_map[book] = doc_df

    doc_string = '/n'

    doc_string = append_prev_messages(doc_string, prev_msgs)
    if books and not doc_dfs_map:
        analytics_data['response'] = "No results found!! Try changing filters"
        analytics_data['response_type'] = 'novels'
        analytics_data['solar_documents_return_count'] = 0
        analytics_data['predicted_book_id'] = predicted_book_id
        insert_conversation_in_db(analytics_data)
        return jsonify({
            'output': "No results found!! Try changing filters",
            'farewell': False,
            'chit_chat': False
        })

    for book, doc_df in doc_dfs_map.items():
        for i in range(min(5, doc_df.shape[0])):
            doc_string += (doc_df.paragraph[i] + ' /n ')

    response = requests.post(RAG_URL, json={
        'query': input_prompt,
        'docs': doc_string,
    })

    if response.status_code != 200:
        print(response.status_code)
        return jsonify(service_down_error(False))

    rag_data = response.json()

    analytics_data['response'] = rag_data['answer']
    analytics_data['response_type'] = 'novels'
    analytics_data['predicted_book_id'] = predicted_book_id
    for book, doc_df in doc_dfs_map.items():
        analytics_data['original_book_id'] = book
        analytics_data['solar_documents_return_count'] = doc_df.shape[0]
        insert_conversation_in_db(analytics_data)

    return jsonify({
        'output': rag_data['answer'],
        'farewell': False,
        'chit_chat': False
    })


@app.route('/analytics', methods=['GET'])
def plot_generator():
    plot_data = {}

    conn = sqlite3.connect('metadata.sqlite')
    cursor = conn.cursor()

    # Generate Timeseries Plot
    cursor.execute('SELECT timestamp FROM message_logs')
    timestamps = [datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f') for row in cursor.fetchall()]
    conversations_per_hour = Counter([timestamp.replace(minute=0, second=0, microsecond=0) for timestamp in timestamps])

    # Prepare data for plotting
    times = list(conversations_per_hour.keys())
    counts = list(conversations_per_hour.values())
    # Plotly data
    conversations_over_time = {
        'data': [{'x': times, 'y': counts, 'type': 'timeseries'}],
        'layout': {'title': 'Conversations Over Time'}
    }
    plot_data['conversations_over_time'] = conversations_over_time

    # Average Number of Conversations Per Session
    cursor.execute("""
        SELECT AVG(conversation_count) AS average_conversations_per_id
        FROM (
            SELECT conversation_id, COUNT(*) AS conversation_count
            FROM message_logs
            GROUP BY conversation_id
        ) AS subquery;
    """)
    plot_data['average_number_of_conversations_in_a_session'] = cursor.fetchall()[0][0]

    # Book Distribution
    cursor.execute('''
        SELECT original_book_id, COUNT(*) as count
        FROM message_logs
        WHERE original_book_id IS NOT NULL
        GROUP BY original_book_id
        ORDER BY count DESC;
    ''')
    book_ids = []
    counts = []
    for row in cursor.fetchall():
        book_ids.append(row[0])
        counts.append(row[1])

    book_distribution = {
        'data': [{'x': book_ids, 'y': counts, 'type': 'bar'}],
        'layout': {'title': 'Book Distribution'}
    }
    plot_data['book_distribution'] = book_distribution

    # Calcualte Accuracy
    cursor.execute("""
                    SELECT COUNT(*) FROM message_logs
                    WHERE original_book_id IS NOT NULL AND predicted_book_id IS NOT NULL AND original_book_id = predicted_book_id;
                    """)

    matched = cursor.fetchall()[0][0]

    cursor.execute("""
                    SELECT COUNT(*) FROM message_logs
                    WHERE original_book_id IS NOT NULL AND predicted_book_id IS NOT NULL;
                    """)
    total = cursor.fetchall()[0][0]
    book_classifier_accuracy = 0

    if total != 0:
        book_classifier_accuracy = matched / total

    plot_data['book_classifier_accuracy'] = book_classifier_accuracy

    # Response Type Distribution
    cursor.execute("""
        SELECT response_type, COUNT(*) as count
        FROM message_logs
        GROUP BY response_type
        ORDER BY count DESC;
    """)
    rows = cursor.fetchall()
    response_types = []
    counts = []
    for row in rows:
        response_types.append(row[0])
        counts.append(row[1])

    response_distribution = {
        'data': [{'x': response_types, 'y': counts, 'type': 'bar'}],
        'layout': {'title': 'Response Distribution'}
    }
    plot_data['response_distribution'] = response_distribution

    cursor.execute("""
                    SELECT original_book_id, SUM(solar_documents_return_count) as Frequency
                        FROM message_logs
                        WHERE original_book_id IS NOT NULL
                        GROUP BY original_book_id;
                   """)
    book_ids = []
    counts = []

    for row in cursor.fetchall():
        book_ids.append(row[0])
        counts.append(row[1])

    solr_documents_distribution_across_books = {
        'data': [{'x': book_ids, 'y': counts, 'type': 'bar'}],
        'layout': {'title': 'Solr distribution across Books'}
    }

    plot_data['solr_documents_distribution_across_book_distribution'] = solr_documents_distribution_across_books

    cursor.execute("""
                   SELECT AVG(SumOfDocuments) as AvgDocumentsPerConversation
                    FROM (
                        SELECT conversation_id, SUM(solar_documents_return_count) as SumOfDocuments
                        FROM message_logs
                        GROUP BY conversation_id
                    ) as SubQuery;
                   """)

    plot_data['average_number_of_solr_documents_fetched_in_a_session'] = cursor.fetchall()[0][0]

    cursor.execute("""
                   SELECT COUNT(DISTINCT conversation_id) as TotalUniqueConversations
                    FROM message_logs;
                   """)
    plot_data['total_number_of_sessions'] = cursor.fetchall()[0][0]

    conn.close()
    return jsonify(plot_data)


if __name__ == '__main__':
    classifier = pipeline("zero-shot-classification", model="MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli")
    app.run(debug=True, host='0.0.0.0', port=5000)
