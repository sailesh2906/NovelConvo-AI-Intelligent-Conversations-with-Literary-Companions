import sqlite3
conn = sqlite3.connect('metadata.sqlite')
cursor = conn.cursor()

cursor.execute('SELECT * FROM conversation_logs')

for row in cursor.fetchall():
    print(row)

conn.close()