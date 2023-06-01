from playwright.sync_api import sync_playwright


def test_flask_app():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=['--remote-debugging-port=9222'])
        context = browser.new_context()
        page = context.new_page()

        # Відкриття додатку у браузері
        page.goto('http://127.0.0.1:5000')

        # Реєстрація нового користувача
        page.click('text=Register')
        page.fill('input[name="username"]', 'test_user2')
        page.fill('input[name="password"]', 'test_password2')
        page.fill('input[name="email"]', 'test2@example.com')
        page.click('text=Submit')

        # Вхід в систему
        page.click('text=Login')
        page.fill('input[name="username"]', 'test_user2')
        page.fill('input[name="password"]', 'test_password2')
        page.click('text=Submit')

        # Перевірка, чи відображається індексна сторінка
        assert page.title() == 'Welcome to FlaskBlog'

        # Створення нового запису
        page.click('text=New Post')
        page.fill('input[name="title"]', 'Test Post')
        page.fill('textarea[name="content"]', 'This is a test post.')
        page.click('text=Submit')

        # Перевірка, чи відображається сторінка зі створеним записом

        assert page.get_by_text('Test Post')

        # Вихід з системи
        page.click('text=Logout')

        # Закриття браузера
        browser.close()

        print('Test passed: All assertions succeeded.')


# Запуск автотесту
test_flask_app()
