# Zzzgrams API Documentation

## Overview

Zzzgrams is a sleep analysis service that processes baby sleep data from Snoo and generates AI-powered insights using AWS Bedrock. The service is deployed as an AWS Lambda function.

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Snoo API  │───▶│  Zzzgrams   │───▶│   Bedrock   │───▶│     SNS     │
│             │    │   Lambda    │    │     AI      │    │   Topic     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Components

### 1. SnooClient (`src/zzzgrams/clients/snoo_client.py`)

Handles authentication and data retrieval from the Snoo baby sleep tracking API.

**Key Methods:**
- `get_sleep_data(start_time, end_time, as_object=True)`: Retrieves sleep data for a given time range
- `_authorize()`: Handles AWS Cognito and Snoo authentication
- `_generate_snoo_sleep_url(baby_id, start_time, end_time)`: Generates API URLs

**Environment Variables:**
- `SNOO_USERNAME`: Snoo account email
- `SNOO_PASSWORD`: Snoo account password  
- `BABY_ID`: Baby's unique identifier

### 2. BedrockClient (`src/zzzgrams/clients/bedrock_client.py`)

Interfaces with AWS Bedrock for AI-powered sleep insights generation.

**Key Methods:**
- `generate_sleep_insights(sleep_data)`: Generates AI insights from sleep data
- `_create_sleep_prompt(sleep_data)`: Creates prompts for the AI model

**Configuration:**
- Model: `amazon.titan-text-premier-v1:0`
- Region: `us-east-1` (configurable)

### 3. SNSClient (`src/zzzgrams/clients/sns_client.py`)

Publishes sleep analysis results to AWS SNS topics.

**Key Methods:**
- `publish_sleep_analysis(ai_insights, sleep_data)`: Publishes formatted messages
- `_create_sns_message(ai_insights, sleep_data)`: Formats messages for SNS

**Configuration:**
- Topic ARN: `SNS_TOPIC_ARN` environment variable (default: `arn:aws:sns:us-east-1:1234567890:SleepAnalyzerTopic`)
- Subject: `Snoozgram Report`

### 4. SleepAnalyzerService (`src/zzzgrams/services/sleep_analyzer_service.py`)

Main business logic service that orchestrates the sleep analysis workflow.

**Key Methods:**
- `analyze_sleep_data(hours_back=20)`: Main analysis method
- Returns: Dictionary with sleep data, AI insights, and metadata

### 5. SleepData Model (`src/zzzgrams/models/sleep_data.py`)

Data model for baby sleep information.

**Fields:**
- `naps`: Number of naps
- `longestSleep`: Longest sleep session (minutes)
- `totalSleep`: Total sleep time (minutes)
- `daySleep`: Day sleep time (minutes)
- `nightSleep`: Night sleep time (minutes)
- `nightWakings`: Number of night wakings

## Lambda Function

### Entry Point: `lambda/lambda_function.py`

**Handler:** `lambda_handler(event, context)`

**Response Format:**
```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*"
  },
  "body": {
    "sleep_data": {
      "naps": 3,
      "longestSleep": 120.0,
      "totalSleep": 480.0,
      "daySleep": 180.0,
      "nightSleep": 300.0,
      "nightWakings": 2
    },
    "ai_insights": "Great sleep last night! Your little one had a solid 5 hours of night sleep.",
    "sns_published": true,
    "timestamp": "2025-01-01T12:00:00-05:00",
    "success": true
  }
}
```

## Error Handling

The service includes comprehensive error handling:

1. **Snoo API Errors**: Captured and returned in response
2. **Bedrock API Errors**: Gracefully handled with error messages
3. **SNS Publishing Errors**: Logged but don't fail the entire request
4. **General Exceptions**: Caught and returned with error details

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SNOO_USERNAME` | Snoo account email | Yes |
| `SNOO_PASSWORD` | Snoo account password | Yes |
| `BABY_ID` | Baby's unique identifier | Yes |
| `SNS_TOPIC_ARN` | SNS topic ARN for notifications | No (default: arn:aws:sns:us-east-1:1234567890:SleepAnalyzerTopic) |
| `AWS_REGION` | AWS region for services | No (default: us-east-1) |

## Testing

Run tests with:
```bash
python -m pytest tests/
```

Or run individual test files:
```bash
python tests/test_sleep_analyzer_service.py
python tests/test_snoo_client.py
python tests/test_bedrock_client.py
python tests/test_sns_client.py
```

## Local Testing

Test the Lambda function locally:
```bash
python scripts/test_local.py
```

## Deployment

Deploy to AWS Lambda:
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

## Monitoring

The service publishes results to SNS topics for monitoring and notifications. Check the AWS SNS console for message delivery status. 