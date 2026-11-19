from http import HTTPStatus

from behave import given, then, when

from src.builders.user_builder import UserBuilder, unique_username
from src.interactors.user_interactor import UserInteractor
from src.utils.assertions import assert_equals
from src.validators.response_validator import response_json
from src.validators.user_validator import (
    validate_user_created,
    validate_user_deleted,
    validate_user_updated,
)


@given('a user with first name "{first_name}", last name "{last_name}" and status {user_status:d}')
def step_user_with_names(context, first_name, last_name, user_status):
    context.builder = (
        UserBuilder()
        .with_id()
        .with_username(unique_username(f"{first_name}.{last_name}"))
        .with_names(first_name, last_name)
        .with_user_status(user_status)
    )


@given('the user has the email "{email}", password "{password}" and phone "{phone}"')
def step_user_contact(context, email, password, phone):
    context.builder.with_email(email).with_password(password).with_phone(phone)


@given("a user with only a username")
def step_user_only_username(context):
    context.builder = UserBuilder().with_username(unique_username())


@when("I send the request to create the user")
def step_create_user(context):
    context.payload = context.builder.build()
    context.response = UserInteractor().create_user(context.payload)


@then("the creation of the user has been successful")
def step_user_created_successfully(context):
    saved_user = UserInteractor().get_user(context.payload["username"])
    validate_user_created(context.response, context.payload, saved_user)


@given("the user has been created")
def step_user_has_been_created(context):
    """Precondition: reuses the create step and only requires a 200 to continue."""
    step_create_user(context)
    assert_equals(context.response.status_code, HTTPStatus.OK, "POST /user status code")


@when("I update the user's first name to \"{first_name}\" and the email to \"{email}\"")
def step_update_user(context, first_name, email):
    """Looks up the created user and sends it back with the new values.

    PUT /user/{username} requires the full User object: a partial body is accepted
    with a 200 but nothing is updated.
    """
    interactor = UserInteractor()
    username = context.payload["username"]
    found = interactor.get_user(username)
    assert_equals(found.status_code, HTTPStatus.OK, f"GET /user/{username} status code")
    context.payload = {**response_json(found), "firstName": first_name, "email": email}
    context.response = interactor.update_user(username, context.payload)


@then("the update of the user has been successful")
def step_user_updated_successfully(context):
    saved_user = UserInteractor().get_user(context.payload["username"])
    validate_user_updated(context.response, context.payload, saved_user)


@when("I delete the user")
def step_delete_user(context):
    context.response = UserInteractor().delete_user(context.payload["username"])


@then("the deletion of the user has been successful")
def step_user_deleted_successfully(context):
    username = context.payload["username"]
    deleted_user = UserInteractor().get_deleted_user(username)
    validate_user_deleted(context.response, username, deleted_user)
