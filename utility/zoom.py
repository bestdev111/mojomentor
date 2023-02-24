import jwt
from time import time
from datetime import datetime
import json
import requests
# sdk constants
SDK_KEY = 'M84NepfqtGnFwSazyeuxojk1m5CZM3HIJPvH'
SDK_SECRET = 'sFEIOZBCsdOfYPSZPyX0i0zthjKou4NrzVFZ'

# jwt constants
API_KEY = 'Md30n96HTwOUNyZN6xbi_w'
API_SECRET = 'J4WRuZeLlvp8DR0CmnIVy6E1uRBxR89er9X8'

# other constants
BASE_URI = 'https://api.zoom.us/v2'


def gen_zoom_sdk_jwt(zoom_role, meeting_no):
    iat = int(time())
    payload = {
        "appKey": SDK_KEY,
        "sdkKey": SDK_KEY,
        "mn": meeting_no,
        "role": zoom_role,  # 0 to specify participant, 1 to specify host.
        "iat": iat,
        "exp": iat + 600,
        "tokenExp": iat + 1800
    }
    encoded_jwt = jwt.encode(payload, SDK_SECRET, algorithm="HS256")
    return encoded_jwt


def gen_zoom_jwt_token():
    payload = {'iss': API_KEY, 'exp': time() + 1800}
    return jwt.encode(payload, API_SECRET, algorithm='HS256')


def create_zoom_meeting():
    meeting_details = {
        "topic": "The title of your zoom meeting",
        "type": 2,
        "start_time": "2022-09-14T10:21:57:00",
        "duration": "45",
        # "timezone": "Europe/Madrid",
        "agenda": "test",
        "recurrence": {"type": 1, "repeat_interval": 1},
        "settings": {
            "host_video": "true",
            "participant_video": "true",
            "join_before_host": "False",
            "mute_upon_entry": "False",
            "watermark": "true",
            "audio": "voip",
            # "auto_recording": "cloud"
        }
    }
    headers = {
        'authorization': 'Bearer ' + gen_zoom_jwt_token(),
        'content-type': 'application/json'
    }
    # res = requests.post(
    #     f'{BASE_URI}/users/raO0h-tTSMObggqW2BpK9A/meetings',
    #     headers=headers, data=json.dumps(meeting_details))
    res = requests.get(
        f'{BASE_URI}/users/raO0h-tTSMObggqW2BpK9A/meetings',
        headers=headers, data=json.dumps(meeting_details))

    print("\n creating zoom meeting ... \n")
    print(res.text)
    # converting the output into json and extracting the details
    data = json.loads(res.text)
    # join_URL = data["join_url"]
    # meetingPassword = data["password"]

    # print(
    #     f'\n here is your zoom meeting link {join_URL} and your \
    #     password: "{meetingPassword}"\n')


def create_zoom_user():
    user_details = {
        "action": "create",
        "user_info": {
            "email": "rajpankajkumar881@gmail.com",
            "first_name": "Pankaj",
            "last_name": "Raj",
            "password": "Raj@123",
            "type": 1,
            "feature": {
                # "zoom_phone": True,
                "zoom_phone": False,
                "zoom_one_type": 16
            },
            "plan_united_type": "1"
        }
    }
    headers = {
        'authorization': 'Bearer ' + gen_zoom_jwt_token(),
        'content-type': 'application/json'
    }
    # res = requests.post(
    #     f'{BASE_URI}/users',
    #     headers=headers, data=json.dumps(user_details))
    res = requests.get(f'{BASE_URI}/users?status=active', headers=headers)

    print("\n creating zoom meeting ... \n")
    print(res.text)
