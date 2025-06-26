import json
from snoo_client import SnooClient
from datetime import datetime, timedelta
import pytz
from dataclasses import asdict
from bedrock_client import BedrockClient
from sns_client import SNSClient


def lambda_handler(event, context):
    """
    AWS Lambda function handler
    
    Args:
        event: The event data passed to the function
        context: Runtime information provided by AWS Lambda
        
    Returns:
        dict: Response object with status code and body
    """
    try:
        # Initialize clients
        snoo_client = SnooClient()
        bedrock_client = BedrockClient()
        sns_client = SNSClient()
        
        # Get time range for sleep data
        eastern = pytz.timezone('America/New_York')
        now = datetime.now(eastern)
        twelve_hours_ago = now - timedelta(hours=20)
        start_time = twelve_hours_ago.strftime('%Y-%m-%dT%H:%M:%S')
        end_time = now.strftime('%Y-%m-%dT%H:%M:%S')

        # Get sleep data from Snoo
        sleep_data = snoo_client.get_sleep_data(start_time=start_time, end_time=end_time)
        sleep_data_dict = asdict(sleep_data)
        
        # Generate AI insights using Bedrock
        ai_insights = bedrock_client.generate_sleep_insights(sleep_data_dict)
        
        # Publish to SNS topic
        sns_success = sns_client.publish_sleep_analysis(ai_insights, sleep_data_dict)

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'sleep_data': sleep_data_dict,
                'ai_insights': ai_insights,
                'sns_published': sns_success,
                'timestamp': now.isoformat()
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        } 