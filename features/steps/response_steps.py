"""Generic response validations, reusable by any feature."""
from behave import then

from src.validators.response_validator import (
    content_type_error,
    field_error,
    response_json,
    schema_error,
)


def _assert_ok(error: str | None) -> None:
    assert error is None, error


@then("the response status code should be {status_code:d}")
def step_status_code(context, status_code):
    actual = context.response.status_code
    assert actual == status_code, (
        f"Expected status {status_code}, got {actual}. Body: {context.response.text}"
    )


@then('the response content type should be "{content_type}"')
def step_content_type(context, content_type):
    _assert_ok(content_type_error(context.response, content_type))


@then("the response body should match the {schema_name} schema")
def step_schema(context, schema_name):
    _assert_ok(schema_error(response_json(context.response), schema_name))


@then('the response field "{path}" should match the request')
def step_field_matches_request(context, path):
    _assert_ok(field_error(context.payload, response_json(context.response), path))
