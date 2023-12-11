import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('metadata.sqlite')

# Create a cursor object
cursor = conn.cursor()

# Copy data from conversation_logs to conversation_logs2
cursor.execute('''
    INSERT INTO conversation_logs2 (timestamp, conversation_id, prompt, response, original_book_id, predicted_book_id, response_type, solar_documents_return_count)
    SELECT timestamp, conversation_id, prompt, response, original_book_id, predicted_book_id, response_type, solar_documents_return_count
    FROM conversation_logs
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

"Data copied successfully from 'conversation_logs' to 'conversation_logs2'."