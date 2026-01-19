from dotenv import load_dotenv
import requests
import time
import datetime
import os
import base64

load_dotenv()

class Mpesa:

    def __init__(self):
        self.consumer_key = os.getenv("CONSUMER_KEY")
        self.consumer_secret = os.getenv("CONSUMER_SECRET")
        self.access_token = ""
        self.expires_at = 0

    def token_cache(self):

        if time.time() < self.expires_at:
            return self.access_token
        else:
            return self.get_access_token()

    def get_access_token(self):

        response = requests.get(
            url="https://sandbox.safaricom.co.ke/oauth/v1/generate",
            headers={
            "Authorization": "Basic eVNPeFFuZDBBakZQWFFtajFxcHVXT043dVdxNkE1ZUpBb05LYkdqU0RmdE1XUDVxOk5EYnZXNDNSdEVqdVlMZVFnY2R2QUVoa2F5eDFPSEE3eHlvRUNBVkpEV1lobzFUWkpidEsyZ0U5dHQ0UEc1SEg"
        },
            params={
            "grant_type":"client_credentials"
        }
        )

        self.access_token = response.json()["access_token"]
        self.expires_at = (time.time() + int(response.json()["expires_in"]) - 45)
        return self.access_token

    def stk_push(self):

        business_short_code = 174379
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        encode_bytes = base64.b64encode(
            f'{business_short_code} + {timestamp} + {os.getenv("EXPRESS_PASSKEY")}'.encode("utf-8")
        )
        password = encode_bytes.decode("utf-8")

        response = requests.post(
            url="https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
            headers={
                "Authorization":f"Bearer {self.access_token}",
                "Content-Type":"application/json"
            },
            json={
                "BusinessShortCode":business_short_code,
                "Password":password,
                "Timestamp": timestamp,
                "TransactionType":"CustomerPayBillOnline",
                "Amount":1,
                "PartyA":254743277086,
                "PartyB":business_short_code,
                "PhoneNumber":254743277087,
                "CallBackUrl":"",
                "AccountReference":"accountref"
            }
        )

        return response.json()
