import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from zzzgrams.clients.bedrock_client import BedrockClient


class TestBedrockClient(unittest.TestCase):
    """Test cases for BedrockClient"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = BedrockClient()
    
    def test_init(self):
        """Test client initialization"""
        client = BedrockClient(region_name='us-west-2')
        self.assertEqual(client.model_id, "amazon.titan-text-premier-v1:0")
    
    @patch('boto3.client')
    def test_generate_sleep_insights_success(self, mock_boto3_client):
        """Test successful sleep insights generation"""
        # Mock Bedrock client
        mock_bedrock = Mock()
        mock_boto3_client.return_value = mock_bedrock
        
        # Mock response
        mock_response = Mock()
        mock_response['body'].read.return_value = '{"results": [{"outputText": "Great sleep!"}]}'
        mock_bedrock.invoke_model.return_value = mock_response
        
        # Create client with mocked boto3
        client = BedrockClient()
        client.bedrock = mock_bedrock
        
        # Test data
        sleep_data = {
            'nightSleep': 300,
            'nightWakings': 2
        }
        
        result = client.generate_sleep_insights(sleep_data)
        
        # Assertions
        self.assertEqual(result, "Great sleep!")
        
        # Verify Bedrock was called correctly
        mock_bedrock.invoke_model.assert_called_once()
        call_args = mock_bedrock.invoke_model.call_args
        self.assertEqual(call_args[1]['modelId'], "amazon.titan-text-premier-v1:0")
        
        # Verify request body structure
        import json
        body = json.loads(call_args[1]['body'])
        self.assertIn('inputText', body)
        self.assertIn('textGenerationConfig', body)
        self.assertIn('maxTokenCount', body['textGenerationConfig'])
        self.assertIn('temperature', body['textGenerationConfig'])
    
    @patch('boto3.client')
    def test_generate_sleep_insights_error(self, mock_boto3_client):
        """Test error handling in sleep insights generation"""
        # Mock Bedrock client to raise exception
        mock_bedrock = Mock()
        mock_bedrock.invoke_model.side_effect = Exception("Bedrock API error")
        mock_boto3_client.return_value = mock_bedrock
        
        # Create client with mocked boto3
        client = BedrockClient()
        client.bedrock = mock_bedrock
        
        # Test data
        sleep_data = {
            'nightSleep': 300,
            'nightWakings': 2
        }
        
        result = client.generate_sleep_insights(sleep_data)
        
        # Assertions
        self.assertIn("Error calling Bedrock", result)
        self.assertIn("Bedrock API error", result)
    
    def test_create_sleep_prompt(self):
        """Test sleep prompt creation"""
        sleep_data = {
            'nightSleep': 300,
            'nightWakings': 2
        }
        
        prompt = self.client._create_sleep_prompt(sleep_data)
        
        # Verify prompt contains expected elements
        self.assertIn("300", prompt)  # nightSleep value
        self.assertIn("2", prompt)    # nightWakings value
        self.assertIn("baby sleep data", prompt.lower())
        self.assertIn("fun, friendly message", prompt.lower())
    
    def test_create_sleep_prompt_missing_data(self):
        """Test sleep prompt creation with missing data"""
        sleep_data = {
            'nightSleep': 0,
            'nightWakings': 0
        }
        
        prompt = self.client._create_sleep_prompt(sleep_data)
        
        # Verify prompt handles missing data gracefully
        self.assertIn("0", prompt)  # Default values
        self.assertIn("baby sleep data", prompt.lower())


if __name__ == '__main__':
    unittest.main() 