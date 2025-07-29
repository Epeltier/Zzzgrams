import json
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import the lambda function
try:
    from lambda.lambda_function import lambda_handler
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

# Mock context object
class MockContext:
    def get_remaining_time_in_millis(self):
        return 30000  # 30 seconds

def test_lambda_function():
    """Test the lambda function locally"""
    
    # Sample event data (you can modify this based on your needs)
    test_event = {
        "httpMethod": "GET",
        "path": "/hello",
        "headers": {},
        "queryStringParameters": None,
        "body": None
    }
    
    # Create mock context
    context = MockContext()
    
    try:
        # Call the lambda function
        response = lambda_handler(test_event, context)
        
        print("✅ Lambda function executed successfully!")
        print(f"Status Code: {response['statusCode']}")
        print(f"Headers: {response['headers']}")
        print(f"Body: {response['body']}")
        
        # Parse and pretty print the JSON body
        body_json = json.loads(response['body'])
        print(f"\nParsed Response:")
        print(json.dumps(body_json, indent=2))
        
    except Exception as e:
        print(f"❌ Error testing lambda function: {e}")

if __name__ == "__main__":
    test_lambda_function() 