import json
from datetime import datetime, timedelta
import pytz
from dataclasses import asdict
from typing import Dict, Any

from ..clients.snoo_client import SnooClient
from ..clients.bedrock_client import BedrockClient
from ..clients.sns_client import SNSClient
from ..utils.text_cleaner import clean_text_for_json


class SleepAnalyzerService:
    """Service class for sleep analysis business logic"""
    
    def __init__(self):
        self.snoo_client = SnooClient()
        self.bedrock_client = BedrockClient()
        self.sns_client = SNSClient()
        self.timezone = pytz.timezone('America/New_York')
    
    def analyze_sleep_data(self, hours_back: int = 20) -> Dict[str, Any]:
        """
        Main method to analyze sleep data and generate insights
        
        Args:
            hours_back: Number of hours to look back for sleep data
            
        Returns:
            Dict containing sleep data, AI insights, and metadata
        """
        try:
            # Get time range for sleep data
            now = datetime.now(self.timezone)
            start_time = (now - timedelta(hours=hours_back)).strftime('%Y-%m-%dT%H:%M:%S')
            end_time = now.strftime('%Y-%m-%dT%H:%M:%S')

            # Get sleep data from Snoo
            sleep_data = self.snoo_client.get_sleep_data(start_time=start_time, end_time=end_time)
            sleep_data_dict = asdict(sleep_data)
            
            # Generate AI insights using Bedrock
            ai_insights = self.bedrock_client.generate_sleep_insights(sleep_data_dict)
            
            # Clean the AI insights for JSON serialization
            cleaned_ai_insights = clean_text_for_json(ai_insights)
            
            # Publish to SNS topic
            sns_success = self.sns_client.publish_sleep_analysis(ai_insights, sleep_data_dict)

            return {
                'sleep_data': sleep_data_dict,
                'ai_insights': cleaned_ai_insights,
                'sns_published': sns_success,
                'timestamp': now.isoformat(),
                'success': True
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'success': False,
                'timestamp': datetime.now(self.timezone).isoformat()
            } 