@user
@update_user

Feature: Update a user
  As a consumer of the PetStore API
  I want to update the first name and email of an existing user
  So that their data stays up to date

  Scenario Outline: Update the first name and email of a user - <first_name> <last_name>
    Given a user with first name "<first_name>", last name "<last_name>" and status <user_status>
    And the user has the email "<email>", password "<password>" and phone "<phone>"
    And the user has been created
    When I update the user's first name to "<new_first_name>" and the email to "<new_email>"
    Then the response status code should be 200
    And the update of the user has been successful

    Examples:
      | first_name | last_name | email                    | password  | phone      | user_status | new_first_name | new_email                    |
      | Ana        | Lopez     | ana.lopez@example.com    | Secret123 | 3001234567 | 1           | Maria          | maria.lopez@example.com      |
      | Carlos     | Perez     | carlos.perez@example.com | P@ssw0rd! | 3109876543 | 0           | Andres         | andres.perez@example.com     |
