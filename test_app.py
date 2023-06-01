import unittest
from werkzeug.exceptions import NotFound
from app import app, get_db_connection, load_user, get_post


class BasicTests(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False

        self.app = app.test_client()

        with app.open_resource('schema.sql') as f:
            self.db_connection = get_db_connection()
            self.db_connection.executescript(f.read().decode('utf8'))

        with app.app_context():
            self.db_connection = get_db_connection()
            self.db_connection.execute("DELETE FROM users")
            self.db_connection.execute("DELETE FROM posts")
            self.db_connection.execute("DELETE FROM comments")
            self.db_connection.execute("DELETE FROM SQLITE_SEQUENCE"
                                       " WHERE name='users'")
            self.db_connection.execute("DELETE FROM SQLITE_SEQUENCE"
                                       " WHERE name='posts'")
            self.db_connection.execute("DELETE FROM SQLITE_SEQUENCE"
                                       " WHERE name='comments'")
            self.db_connection.commit()
            self.db_connection.close()

    # executed after each test
    def tearDown(self):
        pass

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to FlaskBlog', response.data)
        self.assertIn(b'FlaskBlog', response.data)

    def test_register(self):
        with app.app_context():
            response = self.app.post('/register', data=dict(
                username="test_user",
                password="password",
                email="test_user@example.com"
            ))
        self.assertEqual(response.status_code, 302)

    def test_login(self):
        with app.app_context():
            self.db_connection = get_db_connection()
            self.db_connection.execute(
                "INSERT INTO users (username, password, email) "
                "VALUES (?, ?, ?)", ('test_user', 'password',
                                     'test_user@example.com')
            )
            self.db_connection.commit()
            self.db_connection.close()
        response = self.app.post('/login', data=dict(
            username="test_user",
            password="password"
        ))
        self.assertEqual(response.status_code, 302)

    def test_post(self):
        with app.app_context():
            self.db_connection = get_db_connection()
            self.db_connection.execute(
                "INSERT INTO users (username, password, email) "
                "VALUES (?, ?, ?)", ('test_user', 'password',
                                     'test_user@example.com')
            )
            self.db_connection.execute(
                "INSERT INTO posts (title, content, created, user_id) "
                "VALUES (?, ?, ?, ?)", ('test title', 'test content',
                                        '2022-01-01', 1)
            )
            self.db_connection.commit()
            self.db_connection.close()
        response = self.app.get('/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'test title', response.data)

    def test_post_not_found(self):
        with self.assertRaises(NotFound):
            get_post(1)

    def test_load_user(self):
        with app.app_context():
            self.db_connection = get_db_connection()
            self.db_connection.execute(
                "INSERT INTO users (username, password, email) "
                "VALUES (?, ?, ?)", ('test_user', 'password',
                                     'test_user@example.com')
            )
            self.db_connection.commit()
            self.db_connection.close()
        user = load_user(1)
        self.assertEqual(user.id, 1)
        self.assertEqual(user.username, 'test_user')
        self.assertTrue(user.is_authenticated())

    def test_comment_route(self):
        post_id = 1
        comment_data = {'comment': 'Test comment'}
        response = self.app.post(f'/{post_id}/comment', data=comment_data)
        # Перевірка статус коду відповіді
        self.assertEqual(response.status_code, 302)
        # Перевірка редиректу на вірний URL
        self.assertEqual(response.headers['Location'], f'/{post_id}')


if __name__ == "__main__":
    unittest.main(verbosity=2)
