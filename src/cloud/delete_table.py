import sqlite3
conn = sqlite3.connect('metadata.sqlite')
cursor = conn.cursor()

cursor.execute('DROP TABLE IF EXISTS message_logs')

conn.commit()
conn.close()