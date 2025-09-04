import json
from typing import Any, Dict

def _parse_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Accepte soit un event "direct" (LocalStack/Invoke), soit un event API Gateway
    où event["body"] peut être une chaîne JSON. Fusionne proprement.
    """
    body = event.get("body")
    if isinstance(body, str):
        try:
            parsed = json.loads(body)
            event = {**event, **parsed}
        except json.JSONDecodeError:
            # body n'est pas du JSON, on l'ignore
            pass
    return event

def _resp(status: int, body: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
    }

def lambda_handler(event, context):
    try:
        event = _parse_event(event if isinstance(event, dict) else {})
        num1 = float(event.get("num1"))
        num2 = float(event.get("num2"))
        operation = (event.get("operation") or "").lower()

        if operation == "add":
            result = num1 + num2
        elif operation == "subtract":
            result = num1 - num2
        elif operation == "multiply":
            result = num1 * num2
        elif operation == "divide":
            if num2 == 0:
                return _resp(400, {"error": "Cannot divide by zero"})
            result = num1 / num2
        else:
            return _resp(400, {"error": "Invalid operation"})

        return _resp(200, {"result": result})

    except (TypeError, ValueError):
        return _resp(400, {"error": "Invalid numbers"})
    except Exception as e:
        return _resp(400, {"error": str(e)})
