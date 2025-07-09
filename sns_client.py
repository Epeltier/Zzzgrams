import json
import boto3
from datetime import datetime
from typing import Dict, Any


class SNSClient:
    """Client for interacting with AWS SNS"""
    
    def __init__(self, region_name: str = 'us-east-1'):
        self.sns = boto3.client('sns', region_name=region_name)
        self.topic_arn = 'arn:aws:sns:us-east-1:982515757790:SleepAnalyzerTopic'
    
    def publish_sleep_analysis(self, ai_insights: str, sleep_data: Dict[str, Any]) -> bool:
        """
        Publish sleep analysis to SNS topic
        
        Args:
            ai_insights: The AI-generated insights
            sleep_data: The sleep data dictionary
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            message = self._create_sns_message(ai_insights, sleep_data)
            
            response = self.sns.publish(
                TopicArn=self.topic_arn,
                Message=message,
                Subject='Snoozgram Report'
            )
            
            print(f"Message published to SNS: {response['MessageId']}")
            return True
            
        except Exception as e:
            print(f"Error publishing to SNS: {str(e)}")
            return False
    
    def _create_sns_message(self, ai_insights: str, sleep_data: Dict[str, Any]) -> str:
        """
        Create a formatted message for SNS
        
        Args:
            ai_insights: The AI-generated insights
            
        Returns:
            str: Formatted message for SNS
        """
        # Format sleep data for readability
        sleep_summary = f"""
        Sleep Data Summary:
        • Number of naps: {sleep_data.get('naps', 0)}
        • Longest sleep session: {sleep_data.get('longestSleep', 0)} minutes
        • Total sleep time: {sleep_data.get('totalSleep', 0)} minutes
        • Day sleep: {sleep_data.get('daySleep', 0)} minutes
        • Night sleep: {sleep_data.get('nightSleep', 0)} minutes
        • Night wakings: {sleep_data.get('nightWakings', 0)}

        Snooz Insights:
        {ai_insights}
                """.strip()
        
        return sleep_summary 