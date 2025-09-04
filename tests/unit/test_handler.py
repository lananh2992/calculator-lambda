import json
import pytest
from lambda_function import lambda_handler

def parse_body(resp):
    assert "statusCode" in resp
    body = resp.get("body")
    # Le handler renvoie toujours un JSON stringifié
    try:
      data = json.loads(body)
    except Exception:
      pytest.fail(f"Body not JSON: {body}")
    return resp["statusCode"], data

@pytest.mark.parametrize("payload, expected", [
    ({"num1":"2","num2":"3","operation":"add"},       5),
    ({"num1":"5","num2":"3","operation":"subtract"},  2),
    ({"num1":"4","num2":"3","operation":"multiply"}, 12),
    ({"num1":"10","num2":"2","operation":"divide"},   5),
])
def test_ok_operations(payload, expected):
    resp = lambda_handler(payload, None)
    status, data = parse_body(resp)
    assert status == 200
    assert data["result"] == expected

def test_divide_by_zero():
    resp = lambda_handler({"num1":"1","num2":"0","operation":"divide"}, None)
    status, data = parse_body(resp)
    assert status == 400
    assert data["error"] == "Cannot divide by zero"

def test_invalid_operation():
    resp = lambda_handler({"num1":"1","num2":"2","operation":"pow"}, None)
    status, data = parse_body(resp)
    assert status == 400
    assert data["error"] == "Invalid operation"

def test_invalid_numbers():
    resp = lambda_handler({"num1":"x","num2":"2","operation":"add"}, None)
    status, data = parse_body(resp)
    assert status == 400
    assert data["error"] == "Invalid numbers"