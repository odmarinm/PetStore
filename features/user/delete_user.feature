@user
@delete_user

Feature: Delete a user
  As a consumer of the PetStore API
  I want to delete an existing user
  So that it can no longer operate in the store

  Scenario Outline: Delete a user - <first_name> <last_name>
    Given a user with first name "<first_name>", last name "<last_name>" and status <user_status>
    And the user has the email "<email>", password "<password>" and phone "<phone>"
    And the user has been created
    When I delete the user
    Then the response status code should be 200
    And the deletion of the user has been successful

    Examples:
      | first_name | last_name | email                    | password  | phone      | user_status |
      | Ana        | Lopez     | ana.lopez@example.com    | Secret123 | 3001234567 | 1           |
      | Carlos     | Perez     | carlos.perez@example.com | P@ssw0rd! | 3109876543 | 0           |
