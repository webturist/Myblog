import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)",
            ('First Post', 'Content for the first post', 1)
            )

cur.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)",
            ('Second Post', 'Content for the second post', 1)
            )

connection.commit()
connection.close()
