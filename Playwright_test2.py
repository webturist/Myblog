import sys
from playwright.sync_api import Playwright, sync_playwright


def run(playwright_instance: Playwright) -> None:
    browser = playwright_instance.chromium.launch(
        args=['--remote-debugging-port=9222'], headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Відкриття додатку у браузері
    page.goto("http://127.0.0.1:5000/")

    # Реєстрація нового користувача
    page.get_by_role("link", name="Register").click()
    page.get_by_label("Username:").click()
    page.get_by_label("Username:").fill("test")
    page.get_by_label("Username:").press("Tab")
    page.get_by_label("Email:").fill("email@com.ua")
    page.get_by_label("Email:").press("Tab")
    page.get_by_label("Password:").fill("pass")
    page.get_by_role("button", name="Submit").click()
    sys.stderr.write('New User has been created\n')

    try:
        assert page.query_selector('text="You have '
                                   'successfully registered!"') is not None
        sys.stderr.write('Test passed: registration '
                         'success message displayed correctly\n')
    except IOError:
        sys.stderr.write('Error: registration '
                         'success message not displayed correctly\n')

    if page.get_by_text('Username already exists. '
                        'Please choose a different one.'):
        page.get_by_role("link", name="Login").click()

    # Вхід в систему
    page.get_by_label("Username:").click()
    page.get_by_label("Username:").fill("test")
    page.get_by_label("Username:").press("Tab")
    page.get_by_label("Password:").fill("pass")
    page.get_by_role("button", name="Submit").click()
    sys.stderr.write('New user has logged in\n')

    # Перевірка, чи відображається індексна сторінка
    try:
        assert page.title() == 'Welcome to FlaskBlog'
        sys.stderr.write('Test passed: the title '
                         'page is displayed correctly\n')
    except IOError:
        sys.stderr.write('Error: the title page '
                         'not displayed correctly\n')

    # Створення нового запису
    page.locator("#navbarNav").get_by_role("link", name="New Post").click()
    page.get_by_placeholder("Post title").click()
    page.get_by_placeholder("Post title").fill("New Post")
    page.get_by_placeholder("Post title").press("Tab")
    page.get_by_placeholder("Post content").fill("text post")
    page.get_by_role("button", name="Submit").click()
    sys.stderr.write('New Post has been created\n')
    page.locator("div").filter(
        has_text="Welcome to FlaskBlog")\
        .get_by_role("link", name="New Post").first.click()

    # Перевірка, чи відображається сторінка зі створеним записом
    try:
        assert page.title() == 'New Post by test'
        sys.stderr.write('Test passed: New Post is displayed correctly\n')
    except IOError:
        sys.stderr.write('Error: New Post not displayed correctly\n')

    # Видалення цього запису
    # page.locator("div").filter(has_text="Welcome to
    # FlaskBlog").get_by_role("link", name="New Post").click()
    # page.get_by_role("link", name="Edit").click()
    # page.get_by_role("button", name="Delete Post").click()
    # page.once("dialog", lambda dialog: dialog.dismiss())
    # page.get_by_text("\"New post\" was successfully deleted!").click()

    # Редагування даних користувача
    page.get_by_role("link", name="FlaskBlog").click()
    page.get_by_role("link", name="Profile").click()
    page.get_by_role("link", name="Edit Profile").click()
    page.get_by_label("Username:").click()
    page.get_by_label("Username:").fill("test2")
    page.get_by_label("Email:").click()
    page.get_by_label("Email:").fill("test@com.ua")
    page.get_by_role("button", name="Submit").click()
    sys.stderr.write('User has changed the data\n')

    # Вихід з системи
    page.get_by_role("link", name="Logout").click()

    # Закриття браузера
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
