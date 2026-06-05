import boto3
import json
import os

# Model ID from environment variable (set in Lambda config)
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "amazon.nova-micro-v1:0")

def call_bedrock(prompt: str) -> str:
    """
    Invokes Amazon Bedrock via Boto3.
    When Lambda is inside a VPC with a VPC Endpoint configured for
    'com.amazonaws.<region>.bedrock-runtime', all traffic stays private —
    no public internet involved.
    """
    client = boto3.client("bedrock-runtime")

    body = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ],
        "inferenceConfig": {
            "maxTokens": 512,
            "temperature": 0.7
        }
    })

    response = client.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=body,
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response["body"].read())
    return result["output"]["message"]["content"][0]["text"]
