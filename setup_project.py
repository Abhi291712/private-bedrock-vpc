import os

files = {
    "lambda/lambda_function.py": '''import json
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
''',

    "lambda/bedrock.py": '''import boto3
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
''',

    "iam_policy.json": '''{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowBedrockInvoke",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": [
        "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-micro-v1:0"
      ]
    },
    {
      "Sid": "AllowVPCNetworking",
      "Effect": "Allow",
      "Action": [
        "ec2:CreateNetworkInterface",
        "ec2:DescribeNetworkInterfaces",
        "ec2:DeleteNetworkInterface"
      ],
      "Resource": "*"
    },
    {
      "Sid": "AllowLogging",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
''',

    "vpc_endpoint_policy.json": '''{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowBedrockAccessFromVPC",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<YOUR_ACCOUNT_ID>:role/<YOUR_LAMBDA_ROLE>"
      },
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": [
        "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-micro-v1:0"
      ]
    }
  ]
}
''',

    ".env.example": '''# Amazon Bedrock
BEDROCK_MODEL_ID=amazon.nova-micro-v1:0

# AWS Region
AWS_DEFAULT_REGION=us-east-1

# VPC Endpoint (optional override for local testing)
# BEDROCK_ENDPOINT_URL=https://vpce-xxxx.bedrock-runtime.us-east-1.vpce.amazonaws.com
''',

    ".gitignore": '''# Virtual environment
.venv/
venv/

# uv
.uv/
uv.lock

# Environment variables
.env

# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/

# AWS
.aws/

# IDE
.vscode/
.idea/

# Tests
.pytest_cache/
.coverage
htmlcov/
''',
}

def create_project():
    for filepath, content in files.items():
        # Create directories if needed
        dirpath = os.path.dirname(filepath)
        if dirpath:
            os.makedirs(dirpath, exist_ok=True)

        # Write file only if it doesn't exist
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Created: {filepath}")
        else:
            print(f"⏭️  Skipped (exists): {filepath}")

    print("\n🚀 Project scaffold complete!")

if __name__ == "__main__":
    create_project()