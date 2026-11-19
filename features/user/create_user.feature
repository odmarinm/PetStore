@user
@create_user

Feature: Create a user
  As a consumer of the PetStore API
  I want to create a new user
  So that it can operate in the store

  Scenario Outline: Create a user with all fields - <first_name> <last_name>
    Given a user with first name "<first_name>", last name "<last_name>" and status <user_status>
    And the user has the email "<email>", password "<password>" and phone "<phone>"
    When I send the request to create the user
    Then the response status code should be 200
    And the creation of the user has been successful

    Examples:
      | first_name | last_name | email                    | password  | phone      | user_status |
      | Ana        | Lopez     | ana.lopez@example.com    | Secret123 | 3001234567 | 1           |
      | Carlos     | Perez     | carlos.perez@example.com | P@ssw0rd! | 3109876543 | 0           |

  Scenario: Create a user with only the username
    Given a user with only a username
    When I send the request to create the user
    Then the response status code should be 200
    And the creation of the user has been successful
