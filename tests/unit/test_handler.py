import json
import pytest
from lambda_function import lambda_handler

def parse_response(resp):
    """Parse et retourne (statusCode, body_json)"""
    status = resp.get("statusCode")
    try:
        body = json.loads(resp.get("body", "{}"))
    except Exception:
        body = resp.get("body")
    return status, body

@pytest.mark.parametrize("payload, expected", [
    ({"num1":"2","num2":"3","operation":"add"},       5),
    ({"num1":"5","num2":"3","operation":"subtract"},  2),
    ({"num1":"4","num2":"3","operation":"multiply"}, 12),
    ({"num1":"10","num2":"2","operation":"divide"},   5),
])
def test_valid_operations(payload, expected):
    resp = lambda_handler(payload, None)
    status, body = parse_response(resp)
    assert status == 200
    assert body["result"] == expected

def test_divide_by_zero():
    resp = lambda_handler({"num1":"1","num2":"0","operation":"divide"}, None)
    status, body = parse_response(resp)
    assert status == 400
    assert body["error"] == "Cannot divide by zero"

def test_invalid_operation():
    resp = lambda_handler({"num1":"1","num2":"2","operation":"pow"}, None)
    status, body = parse_response(resp)
    assert status == 400
    assert body["error"] == "Invalid operation"

def test_invalid_numbers():
    resp = lambda_handler({"num1":"abc","num2":"2","operation":"add"}, None)
    status, body = parse_response(resp)
    assert status == 400
    assert body["error"] == "Invalid numbers"