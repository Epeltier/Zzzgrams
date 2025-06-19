import json

def lambda_handler(event, context):
    """
    AWS Lambda function handler
    
    Args:
        event: The event data passed to the function
        context: Runtime information provided by AWS Lambda
        
    Returns:
        dict: Response object with status code and body
    """
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'message': 'Hello World!',
            'timestamp': context.get_remaining_time_in_millis()
        })
    } 