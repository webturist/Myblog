import os.path
import sqlite3
import re
import mail as mail_app
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
from flask_login import LoginManager, login_user, logout_user,\
    login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Mail, Message
import jwt

from datetime import datetime, timedelta

app = Flask(__name__)

app.config['SECRET_KEY'] = 'My_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

mail_app = Mail(app)

# Налаштування параметрів для тестового поштового сервера
app.config['MAIL_SERVER'] = 'localhost'
app.config['MAIL_PORT'] = 1050
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = 'sender@example.com'


# try:
#     with open('mail.txt', 'r') as f:
#         lines = f.readlines()
#         if len(lines) < 2:
#             raise Exception('File mail.txt is not in the correct format')
#         app.config['MAIL_USERNAME'] = lines[0].strip()
#         app.config['MAIL_PASSWORD'] = lines[1].strip()
#         app.config['MAIL_SERVER'] = lines[2].strip()
#         app.config['MAIL_PORT'] = lines[3].strip()
#         app.config['MAIL_USE_SSL'] = True
# except Exception as e:
#     app.logger.error(f'Error: {e}')


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    db = get_db_connection()
    with open('schema.sql', 'r') as f:
        db.cursor().executescript(f.read())
    db.commit()


if not os.path.exists('database.db'):
    init_db()


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        db = get_db_connection()
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Перевірка на введення пароля, логіна та електронної пошти
        if not password or not username or not email:
            flash('Please enter all required fields.')
            return redirect(url_for('register'))

        # Перевірка формату емейлу
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, email):
            flash('Invalid email format. Please enter a valid email address.')
            return redirect(url_for('register'))

        existing_user = db.execute('SELECT * FROM users WHERE username = ?',
                                   (username,)).fetchone()
        if existing_user:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('register'))

        db.execute('INSERT INTO users (username, email, password)'
                   ' VALUES (?, ?, ?)',
                   (username, email, generate_password_hash(password)))
        db.commit()
        db.close()
        flash('You have successfully registered!')
        return redirect(url_for('login'))

    return render_template('security/register_user.html')


def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT p.id, p.title, p.content, p.created,'
                        ' p.user_id, u.username as author_name '
                        'FROM posts p JOIN users u ON p.user_id = u.id'
                        ' WHERE p.id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


@login_manager.user_loader
def load_user(user_id):
    db = get_db_connection()
    user = db.execute('SELECT * FROM users WHERE id = ?',
                      (user_id,)).fetchone()
    db.close()
    if user:
        return User(user['id'], user['username'], user['password'])
    else:
        return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = get_db_connection()
        username = request.form['username']
        password = request.form['password']
        user = db.execute('SELECT * FROM users WHERE username = ?',
                          (username,)).fetchone()
        db.close()
        if user and check_password_hash(user['password'], password):
            login_user(User(user['id'], user['username'], user['password']))
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))
    else:
        return render_template('security/login_user.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)


@app.route('/user/<username>')
def user_profile(username):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?',
                        (username,)).fetchone()
    posts = conn.execute('SELECT * FROM posts WHERE user_id = ?',
                         (user['id'],)).fetchall()
    conn.close()
    if user is None:
        abort(404)
    return render_template('security/user_profile.html',
                           user=user, posts=posts)


@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    conn = get_db_connection()
    comments = conn.execute('SELECT * FROM comments WHERE post_id = ?',
                            (post_id,)).fetchall()
    return render_template('post.html', post=post, comments=comments)


@app.route('/<int:post_id>/comment', methods=('POST',))
def comment(post_id):
    if request.method == 'POST':
        comment = request.form['comment']
        conn = get_db_connection()
        conn.execute('INSERT INTO comments (post_id, comment)'
                     ' VALUES (?, ?)',
                     (post_id, comment))
        conn.commit()
        conn.close()
        flash('Comment added successfully')
        return redirect(url_for('post', post_id=post_id))


@app.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user_id = current_user.id

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content, user_id)'
                         ' VALUES (?, ?, ?)',
                         (title, content, user_id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    # Перевірка, чи є поточний користувач автором запису
    if post['user_id'] != current_user.id:
        flash('You are not the author of this post!')
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            flash('Post updated successfully')
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)


@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))


def get_reset_token(user, expires_sec=1800):
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(seconds=expires_sec)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token


def verify_reset_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'],
                             algorithms=['HS256'])
        user_id = payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    db = get_db_connection()
    user = db.execute('SELECT * FROM users WHERE id = ?',
                      (user_id,)).fetchone()
    db.close()
    if user:
        return User(user['id'], user['username'], user['password'])
    else:
        return None


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form['email']
        db = get_db_connection()
        user = db.execute('SELECT * FROM users WHERE email = ?',
                          (email,)).fetchone()
        db.close()
        if user:
            token = get_reset_token(User(user['id'], user['username'],
                                         user['password']))

            msg = Message('Password Reset Request',
                          sender='noreply@demo.com',
                          recipients=[user[3]])
            msg.body = f'''To reset your password, visit the following link:
            {url_for('reset_token', token=token, _external=True)}
            If you did not make this request then simply 
            ignore this email and no changes will be made.
            '''
            try:
                mail_app.send(msg)
                flash('An email has been sent with instructions'
                      ' to reset your password.')
                return redirect(url_for('login'))
            except Exception as e:
                flash(f'An error occurred while sending the email: {e}')
                return redirect(url_for('reset_password'))
        else:
            flash('There is no account with that email.'
                  ' You must register first.')
            return redirect(url_for('register'))
    return render_template('security/reset_password.html')


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    db = get_db_connection()
    user = verify_reset_token(token)
    if not user:
        flash('That is an invalid or expired token')
        return redirect(url_for('reset_request'))
    if request.method == 'POST':
        password = request.form['password']
        db.execute('UPDATE users SET password=? WHERE id=?',
                   (generate_password_hash(password), user.id))
        db.commit()
        db.close()
        flash('Your password has been updated! You are now able to log in')
        return redirect(url_for('login'))
    return render_template('security/resettoken.html', token=token)


@app.route('/change_password', methods=('GET', 'POST'))
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?',
                            (current_user.id,)).fetchone()
        conn.close()

        if not check_password_hash(user['password'], current_password):
            flash('Incorrect current password.')
            return redirect(url_for('change_password'))

        password_hash = generate_password_hash(new_password)
        conn = get_db_connection()
        conn.execute('UPDATE users SET password = ? WHERE id = ?',
                     (password_hash, current_user.id))
        conn.commit()
        conn.close()
        flash('Your password has been updated.')
        return redirect(url_for('index'))

    return render_template('security/change_password.html')


@app.route('/edit_profile', methods=('GET', 'POST'))
@login_required
def edit_profile():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        conn = get_db_connection()
        conn.execute('UPDATE users SET username = ?, email = ? WHERE id = ?',
                     (username, email, current_user.id))
        conn.commit()
        conn.close()
        flash('Your profile has been updated.')
        return redirect(url_for('user_profile', username=username))
    return render_template('security/edit_profile.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)