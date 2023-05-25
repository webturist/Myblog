"""
Initialization script for the database.
"""

import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql', 'r', encoding='utf-8') as f:
    connection.executescript(f.read())

cur = connection.cursor()


cur.execute("DELETE FROM users")
cur.execute("DELETE FROM posts")
cur.execute("DELETE FROM comments")
cur.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='users'")
cur.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='posts'")
cur.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='comments'")


cur.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)",
            ('First Post', 'Content for the first post', 1)
            )

cur.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)",
            ('Second Post', 'Content for the second post', 1)
            )

connection.commit()
connection.close()
