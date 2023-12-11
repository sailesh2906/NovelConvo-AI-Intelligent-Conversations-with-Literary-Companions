import sqlite3
conn = sqlite3.connect('metadata.sqlite')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS message_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        conversation_id TEXT,
        prompt TEXT,
        response TEXT,
        original_book_id Text,
        predicted_book_id Text,
        response_type Text,
        solar_documents_return_count INT
    )
''')

conn.commit()
conn.close()
