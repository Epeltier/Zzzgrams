import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from zzzgrams.clients.sns_client import SNSClient


class TestSNSClient(unittest.TestCase):
    """Test cases for SNSClient"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = SNSClient()
    
    def test_init_default_topic_arn(self):
        """Test client initialization with default topic ARN"""
        client = SNSClient(region_name='us-west-2')
        self.assertEqual(client.topic_arn, 'arn:aws:sns:us-west-2:123456789012:CustomTopic')
    
    @patch.dict(os.environ, {'SNS_TOPIC_ARN': 'arn:aws:sns:us-west-2:123456789012:CustomTopic'})
    def test_init_with_env_variable(self):
        """Test client initialization with environment variable"""
        client = SNSClient(region_name='us-west-2')
        self.assertEqual(client.topic_arn, 'arn:aws:sns:us-west-2:123456789012:CustomTopic')
    
    @patch('boto3.client')
    def test_publish_sleep_analysis_success(self, mock_boto3_client):
        """Test successful sleep analysis publishing"""
        # Mock SNS client
        mock_sns = Mock()
        mock_boto3_client.return_value = mock_sns
        
        # Mock response
        mock_response = {'MessageId': 'test-message-id'}
        mock_sns.publish.return_value = mock_response
        
        # Create client with mocked boto3
        client = SNSClient()
        client.sns = mock_sns
        
        # Test data
        ai_insights = "Great sleep last night! Your little one had a solid 5 hours of night sleep."
        sleep_data = {
            'naps': 3,
            'longestSleep': 120.0,
            'totalSleep': 480.0,
            'daySleep': 180.0,
            'nightSleep': 300.0,
            'nightWakings': 2
        }
        
        result = client.publish_sleep_analysis(ai_insights, sleep_data)
        
        # Assertions
        self.assertTrue(result)
        
        # Verify SNS was called correctly
        mock_sns.publish.assert_called_once()
        call_args = mock_sns.publish.call_args
        self.assertEqual(call_args[1]['TopicArn'], 'arn:aws:sns:us-east-1:1234567890:SleepAnalyzerTopic')
        self.assertEqual(call_args[1]['Subject'], 'Snoozgram Report')
    
    @patch('boto3.client')
    @patch.dict(os.environ, {'SNS_TOPIC_ARN': 'arn:aws:sns:us-west-2:123456789012:CustomTopic'})
    def test_publish_sleep_analysis_with_env_variable(self, mock_boto3_client):
        """Test successful sleep analysis publishing with environment variable"""
        # Mock SNS client
        mock_sns = Mock()
        mock_boto3_client.return_value = mock_sns
        
        # Mock response
        mock_response = {'MessageId': 'test-message-id'}
        mock_sns.publish.return_value = mock_response
        
        # Create client with mocked boto3
        client = SNSClient()
        client.sns = mock_sns
        
        # Test data
        ai_insights = "Great sleep last night!"
        sleep_data = {
            'naps': 3,
            'longestSleep': 120.0,
            'totalSleep': 480.0,
            'daySleep': 180.0,
            'nightSleep': 300.0,
            'nightWakings': 2
        }
        
        result = client.publish_sleep_analysis(ai_insights, sleep_data)
        
        # Assertions
        self.assertTrue(result)
        
        # Verify SNS was called with environment variable topic ARN
        mock_sns.publish.assert_called_once()
        call_args = mock_sns.publish.call_args
        self.assertEqual(call_args[1]['TopicArn'], 'arn:aws:sns:us-west-2:123456789012:CustomTopic')
        self.assertEqual(call_args[1]['Subject'], 'Snoozgram Report')
        
        # Verify message content
        message = call_args[1]['Message']
        self.assertIn('Sleep Data Summary:', message)
        self.assertIn('Number of naps: 3', message)
        self.assertIn('Longest sleep session: 120.0 minutes', message)
        self.assertIn('Total sleep time: 480.0 minutes', message)
        self.assertIn('Day sleep: 180.0 minutes', message)
        self.assertIn('Night sleep: 300.0 minutes', message)
        self.assertIn('Night wakings: 2', message)
        self.assertIn('Snooz Insights:', message)
        self.assertIn(ai_insights, message)
    
    @patch('boto3.client')
    def test_publish_sleep_analysis_error(self, mock_boto3_client):
        """Test error handling in sleep analysis publishing"""
        # Mock SNS client to raise exception
        mock_sns = Mock()
        mock_sns.publish.side_effect = Exception("SNS API error")
        mock_boto3_client.return_value = mock_sns
        
        # Create client with mocked boto3
        client = SNSClient()
        client.sns = mock_sns
        
        # Test data
        ai_insights = "Great sleep!"
        sleep_data = {
            'naps': 3,
            'longestSleep': 120.0,
            'totalSleep': 480.0,
            'daySleep': 180.0,
            'nightSleep': 300.0,
            'nightWakings': 2
        }
        
        result = client.publish_sleep_analysis(ai_insights, sleep_data)
        
        # Assertions
        self.assertFalse(result)
    
    def test_create_sns_message(self):
        """Test SNS message creation"""
        ai_insights = "Great sleep last night!"
        sleep_data = {
            'naps': 3,
            'longestSleep': 120.0,
            'totalSleep': 480.0,
            'daySleep': 180.0,
            'nightSleep': 300.0,
            'nightWakings': 2
        }
        
        message = self.client._create_sns_message(ai_insights, sleep_data)
        
        # Verify message structure
        self.assertIn('Sleep Data Summary:', message)
        self.assertIn('Number of naps: 3', message)
        self.assertIn('Longest sleep session: 120.0 minutes', message)
        self.assertIn('Total sleep time: 480.0 minutes', message)
        self.assertIn('Day sleep: 180.0 minutes', message)
        self.assertIn('Night sleep: 300.0 minutes', message)
        self.assertIn('Night wakings: 2', message)
        self.assertIn('Snooz Insights:', message)
        self.assertIn(ai_insights, message)
    
    def test_create_sns_message_missing_data(self):
        """Test SNS message creation with missing data"""
        ai_insights = "Great sleep!"
        sleep_data = {
            'naps': 0,
            'longestSleep': 0,
            'totalSleep': 0,
            'daySleep': 0,
            'nightSleep': 0,
            'nightWakings': 0
        }
        
        message = self.client._create_sns_message(ai_insights, sleep_data)
        
        # Verify message handles missing data gracefully
        self.assertIn('Sleep Data Summary:', message)
        self.assertIn('Number of naps: 0', message)
        self.assertIn('Longest sleep session: 0 minutes', message)
        self.assertIn('Total sleep time: 0 minutes', message)
        self.assertIn('Day sleep: 0 minutes', message)
        self.assertIn('Night sleep: 0 minutes', message)
        self.assertIn('Night wakings: 0', message)
        self.assertIn('Snooz Insights:', message)
        self.assertIn(ai_insights, message)


if __name__ == '__main__':
    unittest.main() 