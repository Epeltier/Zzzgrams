import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from zzzgrams.services.sleep_analyzer_service import SleepAnalyzerService
from zzzgrams.models.sleep_data import SleepData


class TestSleepAnalyzerService(unittest.TestCase):
    """Test cases for SleepAnalyzerService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = SleepAnalyzerService()
    
    @patch('zzzgrams.services.sleep_analyzer_service.SnooClient')
    @patch('zzzgrams.services.sleep_analyzer_service.BedrockClient')
    @patch('zzzgrams.services.sleep_analyzer_service.SNSClient')
    def test_analyze_sleep_data_success(self, mock_sns, mock_bedrock, mock_snoo):
        """Test successful sleep data analysis"""
        # Mock sleep data
        mock_sleep_data = SleepData(
            naps=3,
            longestSleep=120.0,
            totalSleep=480.0,
            daySleep=180.0,
            nightSleep=300.0,
            nightWakings=2
        )
        
        # Mock AI insights
        mock_ai_response = "Great sleep last night! Your little one had a solid 5 hours of night sleep."
        
        # Configure mocks
        mock_snoo_instance = Mock()
        mock_snoo_instance.get_sleep_data.return_value = mock_sleep_data
        mock_snoo.return_value = mock_snoo_instance
        
        mock_bedrock_instance = Mock()
        mock_bedrock_instance.generate_sleep_insights.return_value = mock_ai_response
        mock_bedrock.return_value = mock_bedrock_instance
        
        mock_sns_instance = Mock()
        mock_sns_instance.publish_sleep_analysis.return_value = True
        mock_sns.return_value = mock_sns_instance
        
        # Create service with mocked clients
        service = SleepAnalyzerService()
        service.snoo_client = mock_snoo_instance
        service.bedrock_client = mock_bedrock_instance
        service.sns_client = mock_sns_instance
        
        # Test the method
        result = service.analyze_sleep_data(hours_back=24)
        
        # Assertions
        self.assertTrue(result['success'])
        self.assertIn('sleep_data', result)
        self.assertIn('ai_insights', result)
        self.assertTrue(result['sns_published'])
        self.assertIn('timestamp', result)
        
        # Verify sleep data structure
        sleep_data = result['sleep_data']
        self.assertEqual(sleep_data['naps'], 3)
        self.assertEqual(sleep_data['longestSleep'], 120.0)
        self.assertEqual(sleep_data['totalSleep'], 480.0)
    
    @patch('zzzgrams.services.sleep_analyzer_service.SnooClient')
    def test_analyze_sleep_data_snoo_error(self, mock_snoo):
        """Test handling of Snoo client errors"""
        # Configure mock to raise exception
        mock_snoo_instance = Mock()
        mock_snoo_instance.get_sleep_data.side_effect = Exception("Snoo API error")
        mock_snoo.return_value = mock_snoo_instance
        
        # Create service with mocked client
        service = SleepAnalyzerService()
        service.snoo_client = mock_snoo_instance
        
        # Test the method
        result = service.analyze_sleep_data()
        
        # Assertions
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('timestamp', result)
        self.assertIn('Snoo API error', result['error'])


if __name__ == '__main__':
    unittest.main() 