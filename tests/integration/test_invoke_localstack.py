import json
import os
import time
import boto3
import botocore
import pytest

LOCALSTACK_URL = os.getenv("LOCALSTACK_URL", "http://localhost:4566")
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
FUNC_NAME = os.getenv("FUNC_NAME", "calculator")

def lambda_client():
    return boto3.client("lambda", region_name=REGION, endpoint_url=LOCALSTACK_URL)

def wait_lambda_api(timeout=60):
    cli = lambda_client()
    start = time.time()
    while time.time() - start < timeout:
        try:
            cli.list_functions()
            return
        except Exception:
            time.sleep(1)
    raise TimeoutError("Lambda API not ready in LocalStack")

def wait_function_exists(func_name: str, timeout=60):
    cli = lambda_client()
    start = time.time()
    while time.time() - start < timeout:
        try:
            cli.get_function(FunctionName=func_name)
            return
        except botocore.exceptions.ClientError as e:
            # Not found yet
            if e.response.get("Error", {}).get("Code") in {"ResourceNotFoundException", "404"}:
                time.sleep(1)
                continue
            raise
        except Exception:
            time.sleep(1)
    raise TimeoutError(f"Function {func_name} not found in LocalStack")

@pytest.mark.parametrize("payload, expected", [
    ({"num1":"2","num2":"3","operation":"add"},       5),
    ({"num1":"5","num2":"3","operation":"subtract"},  2),
    ({"num1":"4","num2":"3","operation":"multiply"}, 12),
    ({"num1":"10","num2":"2","operation":"divide"},   5),
])
def test_lambda_integration(payload, expected):
    wait_lambda_api()
    wait_function_exists(FUNC_NAME)

    cli = lambda_client()
    try:
        resp = cli.invoke(FunctionName=FUNC_NAME, Payload=json.dumps(payload).encode())
    except Exception as e:
        pytest.fail(f"Invoke failed: {type(e).__name__}: {e}")

    assert resp["StatusCode"] == 200
    # La payload de Lambda est un stream bytes → dict de ta Lambda
    body_envelope = json.loads(resp["Payload"].read().decode())
    # Ta Lambda renvoie {"statusCode":..., "headers":..., "body": "<json>"}
    data = json.loads(body_envelope["body"])
    assert data["result"] == expected