import json
import boto3
import re
from typing import Dict, Any


class BedrockClient:
    """Client for interacting with AWS Bedrock models"""
    
    def __init__(self, region_name: str = 'us-east-1'):
        self.bedrock = boto3.client('bedrock-runtime', region_name=region_name)
        self.model_id = "amazon.titan-text-premier-v1:0"
    
    def generate_sleep_insights(self, sleep_data: Dict[str, Any]) -> str:
        """
        Generate AI insights for sleep data using Bedrock
        
        Args:
            sleep_data: Dictionary containing sleep data
            
        Returns:
            str: Generated response from Bedrock
        """
        prompt = self._create_sleep_prompt(sleep_data)
        
        request_body = {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 200,
                "stopSequences": [],
                "temperature": 0.7,
                "topP": 0.9
            }
        }
        
        try:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            raw_response = response_body['results'][0]['outputText']
            
            return raw_response
            
        except Exception as e:
            return f"Error calling Bedrock: {str(e)}"
    
    
    def _create_sleep_prompt(self, sleep_data: Dict[str, Any]) -> str:
        """
        Create a prompt for sleep data analysis
        
        Args:
            sleep_data: Dictionary containing sleep data
            
        Returns:
            str: Formatted prompt for Bedrock
        """
        return f"""
        Based on the following baby sleep data, provide a fun, friendly message for the parent:
        
        Sleep Data:
        - Night sleep: {sleep_data.get('nightSleep', 0)} minutes
        - Night wakings: {sleep_data.get('nightWakings', 0)}
        
        Please provide:
        1. A fun, friendly message for the parent. It consider the data to determine how well and how much the baby slept, especially overnight, and how tired the parent may be because they may have been up all night. Ideally the baby should be sleeping several (6+) hours a night without too many wake ups. 
        2. It should be a short message, just a few lines. It could be a poem, if appropriate. The output should not have any code in it, only human readable text. It should be encouraging and not expressing any concern.
        3. Keep the tone fun and light hearted. It can even be sarcastic ant witty. 
        
        Keep the response concise and parent-friendly.

        An example output if the baby did not sleep many hours at night and had a lot of night wakings could be something like "Wow! that looks like a sleepless night. Hope you can drink lots of coffee today and get some rest" 
        """ 