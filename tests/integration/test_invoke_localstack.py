import json
import os
import time
import boto3
import pytest

LOCALSTACK_URL = os.getenv("LOCALSTACK_URL", "http://localhost:4566")
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
FUNC_NAME = os.getenv("FUNC_NAME", "calculator")

def lambda_client():
    return boto3.client("lambda", region_name=REGION, endpoint_url=LOCALSTACK_URL)

def wait_for_lambda_ready(timeout=60):
    cli = lambda_client()
    start = time.time()
    while time.time() - start < timeout:
        try:
            cli.list_functions()
            return
        except Exception:
            time.sleep(1)
    raise TimeoutError("Lambda API not ready in LocalStack")

@pytest.mark.parametrize("payload, expected", [
    ({"num1":"2","num2":"3","operation":"add"},       5),
    ({"num1":"5","num2":"3","operation":"subtract"},  2),
    ({"num1":"4","num2":"3","operation":"multiply"}, 12),
    ({"num1":"10","num2":"2","operation":"divide"},   5),
])
def test_lambda_integration(payload, expected):
    wait_for_lambda_ready()
    cli = lambda_client()
    resp = cli.invoke(
        FunctionName=FUNC_NAME,
        Payload=json.dumps(payload).encode()
    )
    assert resp["StatusCode"] == 200
    body = json.loads(resp["Payload"].read().decode())
    data = json.loads(body["body"])
    assert data["result"] == expected
