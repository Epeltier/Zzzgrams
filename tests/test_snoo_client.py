import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from zzzgrams.clients.snoo_client import SnooClient
from zzzgrams.models.sleep_data import SleepData


class TestSnooClient(unittest.TestCase):
    """Test cases for SnooClient"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = SnooClient(email='test@example.com', password='password', baby_id='123')
    
    def test_init_with_parameters(self):
        """Test client initialization with parameters"""
        client = SnooClient(email='test@example.com', password='password', baby_id='123')
        self.assertEqual(client.EMAIL, 'test@example.com')
        self.assertEqual(client.PASSWORD, 'password')
        self.assertEqual(client.BABY_ID, '123')
    
    @patch.dict(os.environ, {
        'SNOO_USERNAME': 'env@example.com',
        'SNOO_PASSWORD': 'envpassword',
        'BABY_ID': 'env123'
    })
    def test_init_with_env_vars(self):
        """Test client initialization with environment variables"""
        client = SnooClient()
        self.assertEqual(client.EMAIL, 'env@example.com')
        self.assertEqual(client.PASSWORD, 'envpassword')
        self.assertEqual(client.BABY_ID, 'env123')
    
    def test_generate_snoo_sleep_url(self):
        """Test URL generation for sleep data"""
        start_time = '2025-01-01T00:00:00'
        end_time = '2025-01-01T23:59:59'
        baby_id = '123'
        
        url = self.client._generate_snoo_sleep_url(baby_id, start_time, end_time)
        
        expected_url = (
            'https://api-us-east-1-prod.happiestbaby.com/ss/me/v10/babies/123/'
            'sessions/daily?startTime=2025-01-01T00:00:00&endTime=2025-01-01T23:59:59'
            '&timezone=America/New_York&levels=false'
        )
        self.assertEqual(url, expected_url)
    
    def test_generate_snoo_auth_headers(self):
        """Test auth header generation"""
        token = 'test_token'
        headers = self.client._generate_snoo_auth_headers(token)
        
        self.assertIn('authorization', headers)
        self.assertEqual(headers['authorization'], 'Bearer test_token')
        self.assertIn('content-type', headers)
        self.assertIn('user-agent', headers)
    
    @patch('requests.post')
    def test_auth_amazon(self, mock_post):
        """Test Amazon authentication"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'AuthenticationResult': {
                'AccessToken': 'access_token',
                'IdToken': 'id_token',
                'RefreshToken': 'refresh_token'
            }
        }
        mock_post.return_value = mock_response
        
        result = self.client._auth_amazon()
        
        self.assertEqual(result['AccessToken'], 'access_token')
        self.assertEqual(result['IdToken'], 'id_token')
        self.assertEqual(result['RefreshToken'], 'refresh_token')
    
    @patch('requests.post')
    def test_auth_snoo(self, mock_post):
        """Test Snoo authentication"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'snoo': {
                'token': 'snoo_token'
            }
        }
        mock_post.return_value = mock_response
        
        result = self.client._auth_snoo('id_token')
        
        # Verify the request was made with correct headers
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        headers = call_args[1]['headers']
        self.assertIn('authorization', headers)
        self.assertEqual(headers['authorization'], 'Bearer id_token')
    
    @patch('requests.get')
    @patch.object(SnooClient, '_authorize')
    def test_get_sleep_data_as_object(self, mock_authorize, mock_get):
        """Test getting sleep data as object"""
        # Mock authorization
        mock_authorize.return_value = {
            'aws': {'id': 'id_token'},
            'snoo': 'snoo_token'
        }
        
        # Mock sleep data response
        mock_response = Mock()
        mock_response.json.return_value = {
            'naps': 3,
            'longestSleep': 7200,  # 120 minutes in seconds
            'totalSleep': 28800,   # 480 minutes in seconds
            'daySleep': 10800,     # 180 minutes in seconds
            'nightSleep': 18000,   # 300 minutes in seconds
            'nightWakings': 2
        }
        mock_get.return_value = mock_response
        
        result = self.client.get_sleep_data(as_object=True)
        
        # Verify result is SleepData object
        self.assertIsInstance(result, SleepData)
        self.assertEqual(result.naps, 3)
        self.assertEqual(result.longestSleep, 120.0)  # Converted from seconds
        self.assertEqual(result.totalSleep, 480.0)
        self.assertEqual(result.daySleep, 180.0)
        self.assertEqual(result.nightSleep, 300.0)
        self.assertEqual(result.nightWakings, 2)
    
    @patch('requests.get')
    @patch.object(SnooClient, '_authorize')
    def test_get_sleep_data_as_dict(self, mock_authorize, mock_get):
        """Test getting sleep data as dictionary"""
        # Mock authorization
        mock_authorize.return_value = {
            'aws': {'id': 'id_token'},
            'snoo': 'snoo_token'
        }
        
        # Mock sleep data response
        mock_response = Mock()
        mock_response.json.return_value = {
            'naps': 3,
            'longestSleep': 7200,
            'totalSleep': 28800,
            'daySleep': 10800,
            'nightSleep': 18000,
            'nightWakings': 2
        }
        mock_get.return_value = mock_response
        
        result = self.client.get_sleep_data(as_object=False)
        
        # Verify result is dictionary
        self.assertIsInstance(result, dict)
        self.assertEqual(result['naps'], 3)
        self.assertEqual(result['longestSleep'], 7200)  # Raw seconds
        self.assertEqual(result['totalSleep'], 28800)


if __name__ == '__main__':
    unittest.main() 