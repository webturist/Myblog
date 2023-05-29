Feature: Registration
  As an Un-registered User of the application
  I want to validate the Registration functionality
  In order to check if it works as desired

  Background: User navigates to Registration page
    Given I navigate to the "Registration" page

  @SuccessfulRegistration
  Scenario Outline: Successful Registration using valid credentials
    When I fill in "username" with "<username>"
    And I fill in "email" with "<email>"
    And I fill in "password" with "<password>"
    And I click on the "Submit" button
    Then I should be successfully registered
    And I should land on the "login" page
    And I should see "success" message as "You have successfully registered!"
    And I should see "FlaskBlog" and "Login" links
    Examples:
      | username   | email                   | password   |
      | asdf.asdf  | asdf.asdf@example.com   | Asdf@1234  |

  @DisabledRegistration
  Scenario Outline: Disabled Registration when one of the required fields is left blank
    When I fill in "username" with "<username>"
    And I fill in "email" with "<email>"
    And I fill in "password" with "<password>"
    And I click on the "Submit" button
    Then I should see "<form error>" message for "<input field>" field on "Registration" page

    Examples:
      | username   | email                   | password   | form error                                                   | input field       |
      | NONE       | asdf.asdf@example.com   | Asdf@1234  | Please enter all required fields.                           | username          |
      | asdf       |     NONE                | Asdf@1234  | Please enter all required fields.                          | email             |
      | asdf       | asdf@df                 | Asdf@1234  | Invalid email format. Please enter a valid email address.    | email             |
      | asdf       | asdf.asdf@example.com   |  NONE      | Please enter all required fields.                            | password           |


