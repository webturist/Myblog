import os
import platform
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC


class AppTest(unittest.TestCase):
    def setUp(self):
        # Ініціалізація веб-драйвера (Chrome)
        # Ініціалізація драйвера Selenium
        if platform.system() == 'Windows':
            # Шлях до chromedriver не потрібно вказувати для Windows
            self.driver = webdriver.Chrome(service=Service())
        else:
            # Вкажіть шлях до chromedriver для інших операційних систем
            options = Options()
            options.add_argument('--remote-debugging-port=9222')
            options.add_argument("--headless")
            self.driver = webdriver.Chrome(service=Service(),
                                           options=options)
        self.driver.implicitly_wait(10)  # Задання неявного очікування
        self.driver.get('http://localhost:5000')
        self.screenshot_dir = "screenshot_tests"

    def tearDown(self):
        # Закриття веб-драйвера
        self.driver.quit()

    def save_screenshot(self, name):
        screenshot_dir = os.path.join(os.getcwd(), self.screenshot_dir)
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshot_dir, name)
        self.driver.save_screenshot(screenshot_path)

    def test_1_register_and_login(self):
        # Реєстрація нового користувача
        register_link = self.driver.find_element(By.LINK_TEXT, 'Register')
        register_link.click()

        username_input = self.driver.find_element(By.NAME, 'username')
        email_input = self.driver.find_element(By.NAME, 'email')
        password_input = self.driver.find_element(By.NAME, 'password')
        submit_button = self.driver.find_element(By.XPATH,
                                                 "//input[@type='submit']")

        username_input.send_keys('testuser')
        email_input.send_keys('testuser@example.com')
        password_input.send_keys('testpassword')
        submit_button.click()
        self.save_screenshot('register_success.png')

        # Підтвердження успішної реєстрації
        welcome_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH,"//div[contains(text(), 'You have successfully registered!')]"))
        )
        self.assertIn('You have successfully registered!',
                      welcome_message.text)

        self.login()
        self.save_screenshot('login_success.png')

        # Підтвердження успішного входу
        welcome_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h3[contains(text(),"
                                                      " 'Welcome')]"))
        )
        self.assertIn('Welcome', welcome_message.text)

    def login(self):
        login_link = self.driver.find_element(By.LINK_TEXT, 'Login')
        login_link.click()
        username_input = self.driver.find_element(By.NAME, 'username')
        password_input = self.driver.find_element(By.NAME, 'password')
        submit_button = self.driver.find_element(By.XPATH,
                                                 "//input[@type='submit']")
        username_input.send_keys('testuser')
        password_input.send_keys('testpassword')
        submit_button.click()

    def test_2_create_post(self):
        # Вхід в систему зареєстрованим користувачем
        self.login()

        # Натиснути на посилання для створення нового поста
        create_post_link = self.driver.find_element(By.LINK_TEXT, 'New Post')
        create_post_link.click()

        # Введення коректних даних для створення нового поста
        title_input = self.driver.find_element(By.NAME, 'title')
        content_input = self.driver.find_element(By.NAME, 'content')
        submit_button = self.driver.find_element(By.XPATH,
                                                 "//button[@type='submit']")

        title_input.send_keys('New Post')
        content_input.send_keys('This is the content of the new post')
        submit_button.click()
        self.save_screenshot('New_Post_success.png')

        # Перевірка, що пост успішно створений
        success_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//h2[contains(text(), 'New Post')]"))
        )
        self.assertIn('New Post', success_message.text)

    def test_3_edit_post(self):
        # Вхід в систему зареєстрованим користувачем
        self.login()

        # Натиснути на посилання редагування поста з відповідним ID
        post_id = 1  # ID поста для редагування
        edit_post_link = self.driver.find_element(
            By.XPATH, f"//a[@href='/{post_id}/edit']"
        )
        edit_post_link.click()

        # Введення коректних даних для редагування поста
        title_input = self.driver.find_element(By.NAME, 'title')
        content_input = self.driver.find_element(By.NAME, 'content')
        submit_button = self.driver.find_element(By.XPATH,
                                                 "//button[@type='submit']")

        title_input.clear()
        title_input.send_keys('Updated Post')
        content_input.clear()
        content_input.send_keys('This is the updated content of the post')
        submit_button.click()
        self.save_screenshot('Post_updated_successfully.png')

        # Перевірка, що пост успішно оновлений
        success_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(text(), 'Post updated successfully')]"))
        )
        self.assertIn('Post updated successfully', success_message.text)

    def test_4_add_comment(self):
        # Вхід в систему зареєстрованим користувачем
        self.login()

        # Натиснути на посилання поста, до якого потрібно додати коментар
        post_id = 1  # ID поста, до якого додається коментар
        post_link = self.driver.find_element(By.XPATH,
                                             f"//a[@href='/{post_id}']")
        post_link.click()

        # Введення коментаря
        comment_input = self.driver.find_element(By.NAME,
                                                 'comment')
        submit_button = self.driver.find_element(By.XPATH,
                                                 "//input[@type='submit']")

        comment_text = 'This is a comment'
        comment_input.send_keys(comment_text)
        submit_button.click()
        self.save_screenshot('Comment_added_successfully.png')

        # Перевірка, що коментар успішно доданий
        success_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(text(), 'Comment added successfully')]"))
        )
        self.assertIn('Comment added successfully', success_message.text)

        # Перевірка, що перенаправлення відбувається на сторінку поста
        post_title = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH,
                                            "//h2[contains(text(), 'Post')]"))
        )
        self.assertIsNotNone(post_title)

        # Перевірка, що коментар відображається на сторінці поста
        comment_text_element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//p[contains(text(), '{comment_text}')]"))
        )
        self.assertIsNotNone(comment_text_element)

    def test_5_delete_post(self):
        # Вхід в систему зареєстрованим користувачем
        self.login()

        # Натиснути на посилання редагування поста з відповідним ID
        post_id = 1  # ID поста для видалення
        edit_post_link = self.driver.find_element(
            By.XPATH, f"//a[@href='/{post_id}/edit']"
        )
        edit_post_link.click()

        # Підтвердження видалення
        delete_post_button = self.driver.find_element(
            By.XPATH, "//input[@value='Delete Post']"
        )
        delete_post_button.click()
        alert = self.driver.switch_to.alert
        alert.accept()
        self.save_screenshot('Post_successfully_deleted.png')

        # Перевірка, що пост успішно видалений
        success_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(text(),'was successfully deleted!')]"))
        )
        self.assertIn('was successfully deleted!', success_message.text)


if __name__ == '__main__':
    unittest.main()
