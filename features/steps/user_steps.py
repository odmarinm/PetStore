"""User steps. Given builds the payload, When sends it and stores the response, Then validates."""
from behave import given, then, when

from src.builders.user_builder import UserBuilder, unique_username
from src.interactors.user_interactor import UserInteractor
from src.validators.user_validator import validate_user_created


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
