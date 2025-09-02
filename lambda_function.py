import json

def lambda_handler(event, context):
    try:
        num1 = float(event.get("num1"))
        num2 = float(event.get("num2"))
        operation = event.get("operation")

        if operation == "add":
            result = num1 + num2
        elif operation == "subtract":
            result = num1 - num2
        elif operation == "multiply":
            result = num1 * num2
        elif operation == "divide":
            if num2 == 0:
                return {"statusCode": 400, "body": json.dumps("Cannot divide by zero")}
            result = num1 / num2
        else:
            return {"statusCode": 400, "body": json.dumps("Invalid operation")}

        return {"statusCode": 200, "body": json.dumps({"result": result})}

    except Exception as e:
        return {"statusCode": 400, "body": json.dumps(f"Error: {str(e)}")}
