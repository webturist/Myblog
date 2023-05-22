from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
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

    if page.get_by_text('Username already exists. Please choose a different one.'):
        page.get_by_role("link", name="Login").click()


    # Вхід в систему
    page.get_by_label("Username:").click()
    page.get_by_label("Username:").fill("test")
    page.get_by_label("Username:").press("Tab")
    page.get_by_label("Password:").fill("pass")
    page.get_by_role("button", name="Submit").click()

    # Створення нового запису
    page.locator("#navbarNav").get_by_role("link", name="New Post").click()
    page.get_by_placeholder("Post title").click()
    page.get_by_placeholder("Post title").fill("New Post")
    page.get_by_placeholder("Post title").press("Tab")
    page.get_by_placeholder("Post content").fill("text post")
    page.get_by_role("button", name="Submit").click()


    # Редагування даних користувача
    page.get_by_role("link", name="Profile").click()
    page.get_by_role("link", name="Edit Profile").click()
    page.get_by_label("Username:").click()
    page.get_by_label("Username:").fill("test2")
    page.get_by_label("Email:").click()
    page.get_by_label("Email:").fill("test@com.ua")
    page.get_by_role("button", name="Submit").click()

    # Вихід з системи
    page.get_by_role("link", name="Logout").click()

    # Закриття браузера
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
