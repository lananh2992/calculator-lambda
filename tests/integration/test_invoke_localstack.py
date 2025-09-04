# tests/integration/test_invoke_localstack.py
import json, os, time, boto3, botocore, pytest

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

def wait_function_active(func_name: str, timeout=60):
    cli = lambda_client()
    start = time.time()
    while time.time() - start < timeout:
        try:
            conf = cli.get_function_configuration(FunctionName=func_name)
            state = conf.get("State")
            last = conf.get("LastUpdateStatus")
            if state == "Active" and last == "Successful":
                return
            time.sleep(1)
        except botocore.exceptions.ClientError as e:
            if e.response.get("Error", {}).get("Code") in {"ResourceNotFoundException", "404"}:
                time.sleep(1)
                continue
            raise
    raise TimeoutError(f"Function {func_name} not Active in LocalStack")

@pytest.mark.parametrize("payload, expected", [
    ({"num1":"2","num2":"3","operation":"add"},       5),
    ({"num1":"5","num2":"3","operation":"subtract"},  2),
    ({"num1":"4","num2":"3","operation":"multiply"}, 12),
    ({"num1":"10","num2":"2","operation":"divide"},   5),
])
def test_lambda_integration(payload, expected):
    wait_lambda_api()
    wait_function_active(FUNC_NAME)
    cli = lambda_client()
    resp = cli.invoke(FunctionName=FUNC_NAME, Payload=json.dumps(payload).encode())
    assert resp["StatusCode"] == 200
    envelope = json.loads(resp["Payload"].read().decode())
    data = json.loads(envelope["body"])
    assert data["result"] == expected
