import json
from bedrock import call_bedrock

def lambda_handler(event, context):
    """
    Lambda handler — invokes Amazon Bedrock privately via VPC Endpoint.
    Traffic never leaves the AWS private network.
    """
    prompt = event.get("prompt", "Explain the benefits of cloud security in 2 sentences.")

    response = call_bedrock(prompt)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "prompt": prompt,
            "response": response
        })
    }
