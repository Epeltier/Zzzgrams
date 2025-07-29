# ZzzGrams

Sleep quips from a newborn baby. 

![example snoozgram](/docs/img/snooz.png)


This project sends a daily encouraging message to newborn parents based on the previous night's sleep data from the Snoo bassinet device.

The Snoo data is pulled from an unofficial Snoo API. Amazon Bedrock running the Titan LLM is used to synthesize the message for the parent. 

Example Message:

![example snoozgram](/docs/img/snoozgram_example.png)

## Architecture
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Snoo API  │──▶│  Zzzgrams   │───▶│   Bedrock   │───▶│     SNS    │
│             │    │   Lambda    │    │     AI      │    │   Topic     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Project Structure

```
Zzzgrams/
├── README.md
├── requirements.txt
├── .gitignore
├── tests/
│   ├── __init__.py
│   ├── test_sleep_analyzer_service.py
│   ├── test_snoo_client.py
│   ├── test_bedrock_client.py
│   └── test_sns_client.py
├── src/
│   └── zzzgrams/
│       ├── __init__.py
│       ├── clients/
│       │   ├── __init__.py
│       │   ├── snoo_client.py
│       │   ├── bedrock_client.py
│       │   └── sns_client.py
│       ├── services/
│       │   ├── __init__.py
│       │   └── sleep_analyzer_service.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── sleep_data.py
│       └── utils/
│           ├── __init__.py
│           └── text_cleaner.py
├── lambda/
│   ├── __init__.py
│   └── lambda_function.py
├── scripts/
│   ├── deploy.sh
│   └── test_local.py
└── docs/
    ├── API.md
    └── DEPLOYMENT.md
```

## Quick Start

### Prerequisites

1. **Python 3.9+**
2. **AWS CLI** configured with appropriate permissions
3. **Snoo Account** with API access
4. **AWS Services**: Lambda, SNS, Bedrock, IAM

### Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**
   ```bash
   export SNOO_USERNAME="your-snoo-email@example.com"
export SNOO_PASSWORD="your-snoo-password"
export BABY_ID="your-baby-id"
export SNS_TOPIC_ARN="arn:aws:sns:us-east-1:YOUR-ACCOUNT-ID:SleepAnalyzerTopic"
export AWS_REGION="us-east-1"
   ```

### Local Development

1. **Run tests**
   ```bash
   python -m pytest tests/
   ```

2. **Test Lambda function locally**
   ```bash
   python scripts/test_local.py
   ```

### Deployment

1. **Deploy to AWS Lambda**
   ```bash
   chmod +x scripts/deploy.sh
   ./scripts/deploy.sh
   ```

2. **Follow the complete deployment guide**: See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SNOO_USERNAME` | Snoo account email | Yes |
| `SNOO_PASSWORD` | Snoo account password | Yes |
| `BABY_ID` | Baby's unique identifier | Yes |
| `SNS_TOPIC_ARN` | SNS topic ARN for notifications | No (default: arn:aws:sns:us-east-1:982515757790:SleepAnalyzerTopic) |
| `AWS_REGION` | AWS region for services | No (default: us-east-1) |

### AWS Services Configuration

- **Lambda Function**: `zzzgrams-sleep-analyzer`
- **SNS Topic**: `arn:aws:sns:us-east-1:982515757790:SleepAnalyzerTopic`
- **Bedrock Model**: `amazon.titan-text-premier-v1:0`

## API Response Format

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