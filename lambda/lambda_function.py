import json
import sys
import os

# Add the src directory to the Python path for Lambda
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from zzzgrams.services.sleep_analyzer_service import SleepAnalyzerService


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
        # Initialize the sleep analyzer service
        analyzer_service = SleepAnalyzerService()
        
        # Analyze sleep data (default 20 hours back)
        result = analyzer_service.analyze_sleep_data()
        
        if result['success']:
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(result)
            }
        else:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(result)
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'success': False
            })
        } 