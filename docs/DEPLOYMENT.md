# Zzzgrams Deployment Guide

## Prerequisites

Before deploying Zzzgrams, ensure you have the following:

### 1. AWS Account Setup
- AWS account with appropriate permissions
- AWS CLI installed and configured
- IAM user with Lambda, SNS, and Bedrock permissions

### 2. Required AWS Services
- **AWS Lambda**: For running the sleep analysis function
- **AWS SNS**: For publishing sleep analysis results
- **AWS Bedrock**: For AI-powered insights generation
- **AWS IAM**: For service permissions

### 3. Environment Variables
Set the following environment variables:
```bash
export SNOO_USERNAME="your-snoo-email@example.com"
export SNOO_PASSWORD="your-snoo-password"
export BABY_ID="your-baby-id"
export SNS_TOPIC_ARN="arn:aws:sns:us-east-1:YOUR-ACCOUNT-ID:SleepAnalyzerTopic"
export AWS_REGION="us-east-1"
```

## Deployment Steps

### Step 1: Clone and Setup
```bash
git clone <repository-url>
cd Zzzgrams
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Create AWS Resources

#### 3.1 Create SNS Topic
```bash
aws sns create-topic --name SleepAnalyzerTopic --region us-east-1
```

#### 3.2 Create IAM Role for Lambda
Create a file `lambda-role-policy.json`:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "arn:aws:sns:us-east-1:*:SleepAnalyzerTopic"
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-text-premier-v1:0"
    }
  ]
}
```

Create the role:
```bash
aws iam create-role --role-name ZzzgramsLambdaRole --assume-role-policy-document '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}'

aws iam put-role-policy --role-name ZzzgramsLambdaRole --policy-name ZzzgramsLambdaPolicy --policy-document file://lambda-role-policy.json
```

#### 3.3 Create Lambda Function
```bash
# Create deployment package
./scripts/deploy.sh

# Create Lambda function
aws lambda create-function \
  --function-name zzzgrams-sleep-analyzer \
  --runtime python3.9 \
  --role arn:aws:iam::YOUR-ACCOUNT-ID:role/ZzzgramsLambdaRole \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://zzzgrams-lambda.zip \
  --timeout 30 \
  --memory-size 256 \
      --environment Variables='{
      "SNOO_USERNAME":"your-snoo-email@example.com",
      "SNOO_PASSWORD":"your-snoo-password",
      "BABY_ID":"your-baby-id",
      "SNS_TOPIC_ARN":"arn:aws:sns:us-east-1:YOUR-ACCOUNT-ID:SleepAnalyzerTopic"
    }'
```

### Step 4: Configure Triggers

#### 4.1 EventBridge (CloudWatch Events) Trigger
Create a rule to trigger the Lambda function on a schedule:

```bash
aws events put-rule \
  --name zzzgrams-schedule \
  --schedule-expression "rate(1 hour)" \
  --state ENABLED

aws events put-targets \
  --rule zzzgrams-schedule \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:YOUR-ACCOUNT-ID:function:zzzgrams-sleep-analyzer"

aws lambda add-permission \
  --function-name zzzgrams-sleep-analyzer \
  --statement-id EventBridgeInvoke \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-1:YOUR-ACCOUNT-ID:rule/zzzgrams-schedule


### 1. Test Lambda Function
```bash
# Test locally
python scripts/test_local.py

# Test via AWS CLI
aws lambda invoke \
  --function-name zzzgrams-sleep-analyzer \
  --payload '{}' \
  response.json

cat response.json
```

### 2. Check SNS Messages
```bash
# List SNS topics
aws sns list-topics

# Check recent messages (via AWS Console)
# Go to SNS > Topics > SleepAnalyzerTopic > View recent messages
```
