import unittest
from werkzeug.exceptions import NotFound
from app import app, get_db_connection, load_user, get_post


class BasicTests(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['DATABASE'] = 'test.db'

        self.app = app.test_client()

        with app.open_resource('schema.sql') as f:
            self.db_connection = get_db_connection()
            self.db_connection.executescript(f.read().decode('utf8'))

        with app.app_context():
            self.db_connection = get_db_connection()
            self.db_connection.execute("DELETE FROM users")
            self.db_connection.execute("DELETE FROM posts")
            self.db_connection.execute("DELETE FROM comments")
            self.db_connection.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='users'")
            self.db_connection.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='posts'")
            self.db_connection.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='comments'")
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
                "VALUES (?, ?, ?)", ('test_user', 'password', 'test_user@example.com')
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
                "VALUES (?, ?, ?)", ('test_user', 'password', 'test_user@example.com')
            )
            self.db_connection.execute(
                "INSERT INTO posts (title, content, created, user_id) "
                "VALUES (?, ?, ?, ?)", ('test title', 'test content', '2022-01-01', 1)
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
                "VALUES (?, ?, ?)", ('test_user', 'password', 'test_user@example.com')
            )
            self.db_connection.commit()
            self.db_connection.close()
        user = load_user(1)
        self.assertEqual(user.id, 1)
        self.assertEqual(user.username, 'test_user')
        self.assertTrue(user.is_authenticated())

    def test_edit_post(self):
        with app.app_context():
            self.db_connection = get_db_connection()
            # Add a test user to the database
            self.db_connection.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                                       ('test_user', 'password', 'test_user@example.com'))
            self.db_connection.commit()

            # Add a test post to the database
            self.db_connection.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)",
                                       ('Test Title', 'Test Content', 1))
            self.db_connection.commit()
            self.db_connection.close()

        self.app.post('/login', data=dict(
            username='test_user',
            password='password'
        ), follow_redirects=True)

        # Edit the post
        response = self.app.post('/1/edit', data=dict(
            title='New Title',
            content='New Content'
        ), follow_redirects=True)

        # Check if the response is successful and the post is updated
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Post updated successfully.', response.data)
        self.assertIn(b'New Title', response.data)
        self.assertIn(b'New Content', response.data)

    def test_edit_profile(self):
        with app.app_context():
            self.db_connection = get_db_connection()
            self.db_connection.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                                       ('test_user', 'password', 'test_user@example.com'))
            self.db_connection.commit()
            self.db_connection.close()
        # Log in the test user
        self.app.post('/login', data=dict(
            username='test_user',
            password='password'
        ), follow_redirects=True)

        # Edit the user profile
        response = self.app.post('/edit_profile', data=dict(
            username='new-username',
            email='newemail@example.com'
        ), follow_redirects=True)

        # Check if the response is successful and the user profile is updated
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your profile has been updated.', response.data)
        self.assertIn(b'new-username', response.data)
        self.assertIn(b'newemail@example.com', response.data)

    def test_comment_route(self):
        post_id = 1
        comment_data = {'comment': 'Test comment'}
        response = self.app.post(f'/{post_id}/comment', data=comment_data)
        # Перевірка статус коду відповіді
        self.assertEqual(response.status_code, 302)
        # Перевірка редиректу на вірний URL
        self.assertEqual(response.headers['Location'], f'/{post_id}')

    def test_delete_route(self):
        # Тест для роуту /<int:id>/delete
        post_id = 1
        post_data = {'id': post_id}
        response = self.app.post(f'/{post_id}/delete', data=post_data)
        # Перевірка статус коду відповіді
        self.assertEqual(response.status_code, 302)
        # Перевірка редиректу на вірний URL
        self.assertEqual(response.headers['Location'], 'http://localhost/')


if __name__ == "__main__":
    unittest.main(verbosity=2)
