
from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Ініціалізація веб-драйвера
driver = webdriver.Chrome()



@given('I navigate to the "Registration" page')
def step_navigate_to_registration_page(context):
    # Відкриття сторінки "Registration"
    driver.get("http://127.0.0.1:5000/register")


@when(u'I fill in "{input_field}" with "{value}"')
def step_fill_in_input_field(context, input_field, value):
    # Знаходження елемента поля вводу за назвою
    input_element = driver.find_element(By.NAME, input_field)

    print(f"Input field: {input_field}")
    print(f"Value: {value}")

    # Заповнення поля вводу значенням
    if value == "NONE":
        driver.execute_script("arguments[0].value = '';", input_element)
    else:
        input_element.send_keys(value)



@when('I click on the "Submit" button')
def step_click_register_button(context):
    # Знаходження кнопки "submit" за текстом
    register_button = driver.find_element(By.XPATH, "//input[@type='submit']")

    # Клік на кнопку "submit"
    register_button.click()


@then('I should be successfully registered')
def step_verify_registration_success(context):
    # Очікування успішної реєстрації
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'You have successfully registered!')]"))
    )


@then('I should land on the "login" page')
def step_verify_home_page(context):
    # Перевірка поточної сторінки
    assert "login" in driver.current_url


@then('I should see "{message}" message as "{expected_message}"')
def step_verify_message(context, message, expected_message):
    # Знаходження елемента з повідомленням за текстом
    message_element = driver.find_element(By.XPATH, f"//*[contains(text(), '{message}')]")

    # Перевірка очікуваного повідомлення
    assert expected_message in message_element.text


@then('I should see "{link1}" and "{link2}" links')
def step_verify_links(context, link1, link2):
    # Знаходження елементів посилань за текстом
    link1_element = driver.find_element(By.LINK_TEXT, link1)
    link2_element = driver.find_element(By.LINK_TEXT, link2)

    # Перевірка наявності посилань
    assert link1_element.is_displayed() and link2_element.is_displayed()


@then('I should see "{error_message}" message for "{input_field}" field on "Registration" page')
def step_verify_form_error_message(context, error_message, input_field):
    # Знаходження елемента з повідомленням про помилку за текстом
    error_message_element = driver.find_element(By.XPATH, f"//div[contains(text(), '{error_message}')]")

    # Перевірка очікуваного повідомлення про помилку
    assert error_message in error_message_element.text


# Закриття веб-драйвера після завершення виконання тестів
def after_all(context):
    driver.quit()
