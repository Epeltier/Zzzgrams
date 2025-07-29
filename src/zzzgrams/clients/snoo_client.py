import requests
import json
import urllib
from datetime import datetime as dt
import os
from typing import Optional, Any
from ..models.sleep_data import SleepData


class SnooClient:
    """Client for interacting with Snoo baby sleep tracking API"""
    
    def __init__(self, email=None, password=None, baby_id=None):
        self.EMAIL = email or os.getenv('SNOO_USERNAME')
        self.PASSWORD = password or os.getenv('SNOO_PASSWORD')
        self.BABY_ID = baby_id or os.getenv('BABY_ID')

        self.aws_auth_url = 'https://cognito-idp.us-east-1.amazonaws.com/'
        self.snoo_auth_url = 'https://api-us-east-1-prod.happiestbaby.com/us/me/v10/pubnub/authorize'
        self.snoo_devices_url = 'https://api-us-east-1-prod.happiestbaby.com/hds/me/v11/devices'
        self.snoo_data_url = 'https://happiestbaby.pubnubapi.com'
        self.snoo_data_endpoint = 'v2/subscribe/sub-c-97bade2a-483d-11e6-8b3b-02ee2ddab7fe'
        self.aws_auth_hdr = {
            'x-amz-target': 'AWSCognitoIdentityProviderService.InitiateAuth',
            'accept-language': 'US',
            'content-type': 'application/x-amz-json-1.1',
            'accept-encoding': 'gzip',
            'user-agent': 'okhttp/4.12.0',
            'accept': 'application/json',
        }
        self.snoo_auth_hdr = {
            'accept-language': 'US',
            'content-type': 'application/json; charset=UTF-8',
            'accept-encoding': 'gzip',
            'user-agent': 'okhttp/4.12.0',
            'accept': 'application/json',
        }
        self.snoo_data_hdr = {
            'connection': 'keep-alive',
            'accept-encoding': 'gzip',
            'user-agent': 'okhttp/4.12.0'
        }
        self.aws_auth_data = {
            "AuthParameters": {
                "PASSWORD": self.PASSWORD,
                "USERNAME": self.EMAIL,
            },
            "AuthFlow": "USER_PASSWORD_AUTH",
            "ClientId": "6kqofhc8hm394ielqdkvli0oea",
        }
        self.snoo_auth_data = {
            "advertiserId": "",
            "appVersion": "1.8.7",
            "device": "panther",
            "deviceHasGSM": True,
            "locale": "en",
            "os": "Android",
            "osVersion": "14",
            "platform": "Android",
            "timeZone": "America/New_York",
            "userCountry": "US",
            "vendorId": "eyqurgwYQSqmnExnzyiLO5"
        }

    def _encode(self, data):
        return urllib.parse.quote_plus(data)

    def _generate_snoo_auth_headers(self, amz_token):
        hdrs = self.snoo_auth_hdr.copy()
        hdrs['authorization'] = f'Bearer {amz_token}'
        return hdrs

    def _generate_snoo_sleep_url(self, babyId, startTime, endTime):
        url = f'https://api-us-east-1-prod.happiestbaby.com/ss/me/v10/babies/{babyId}/sessions/daily?startTime={startTime}&endTime={endTime}&timezone=America/New_York&levels=false'
        return url

    def _auth_amazon(self):
        r = requests.post(self.aws_auth_url, data=json.dumps(self.aws_auth_data), headers=self.aws_auth_hdr)
        resp = r.json()
        result = resp['AuthenticationResult']
        return result

    def _auth_snoo(self, id_token):
        hdrs = self._generate_snoo_auth_headers(id_token)
        r = requests.post(self.snoo_auth_url, data=json.dumps(self.snoo_auth_data), headers=hdrs)
        return r

    def _authorize(self):
        amz = self._auth_amazon()
        access = amz['AccessToken']
        _id = amz['IdToken']
        ref = amz['RefreshToken']
        snoo = self._auth_snoo(_id)
        snoo_token = snoo.json()['snoo']['token']
        return {'aws': {'access': access, 'id': _id, 'refresh': ref}, 'snoo': snoo_token}

    def get_sleep_data(self, start_time='2025-06-21T00:00:00', end_time='2025-06-21T23:59:59', as_object: bool = True) -> Any:
        """
        Get sleep data from Snoo API
        
        Args:
            start_time: Start time for data retrieval
            end_time: End time for data retrieval
            as_object: Whether to return as SleepData object or raw dict
            
        Returns:
            SleepData object or dict depending on as_object parameter
        """
        auth = self._authorize()
        id_token = auth['aws']['id']
        hdrs = self._generate_snoo_auth_headers(id_token)
        url = self._generate_snoo_sleep_url(self.BABY_ID, start_time, end_time)
        r = requests.get(url, headers=hdrs, timeout=5)
        data = r.json()
        if as_object:
            return SleepData.from_dict(data)
        return data 