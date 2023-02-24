import string
import random
import time
import base64
from .models import LinkToken
from datetime import date, timedelta, datetime


def gen_link_token(user):
    # generating random strings using random.choices()
    random_str = ''.join(random.choices(string.ascii_letters, k=40))
    curr_time = time.time()
    time_bytes = f"{curr_time}".encode('ascii')
    time_base64_bytes = base64.b64encode(time_bytes)
    base64_time_str = time_base64_bytes.decode('ascii')
    token = random_str + base64_time_str
    # deleting all existing tokens
    LinkToken.objects.filter(user_id=user.id).delete()
    # creating new tokens
    LinkToken.objects.create(
        user_id=user.id, expire_in=(curr_time + 600), token=token
    )
    return token


def verify_link_token(token):
    try:
        link_token = LinkToken.objects.get(token=token)
        expire_in = float(link_token.expire_in)
        link_token.delete()
        if time.time() <= expire_in:
            return 200, 'Email verified'
        else:
            return 401, 'Link expired'
    except LinkToken.DoesNotExist:
        return 404, 'Link does not exits'
    except LinkToken.MultipleObjectsReturned:
        return 500, 'Something went wrong.'


def seconds_to_hms(seconds: float):
    seconds = seconds
    secs = int(seconds % 60)
    minuts = int(seconds/60)
    mins = minuts % 60
    hours = int(minuts/60)
    return hours, mins, secs


def time_offset_to_mins(time_offset):
    hr, min = time_offset[1:].split(':')
    offset_mins = (int(hr) * 60) + int(min)
    return (-offset_mins) if time_offset[0] == '-' else offset_mins


def time_to_mins(time_str):
    hr, min = time_str.split(':')
    return (int(hr) * 60) + int(min)

def mins_to_time(mins):
    return f"{str(int(mins/60)).zfill(2)}:{str(int(mins%60)).zfill(2)}"

def time_str_to_utc_time_str(time_str, offset_str):
    today = datetime.utcnow().date()
    in_hr, in_min = time_str.split(':')
    of_hr, of_min = offset_str[1:].split(':')
    temp_date = datetime(today.year, today.month, today.day, int(in_hr), int(in_min))
    if offset_str[0] == '-':
        req_date = temp_date + timedelta(hours=int(of_hr), minutes=int(of_min))
    else:
        req_date = temp_date - timedelta(hours=int(of_hr), minutes=int(of_min))
    return f"{str(req_date.hour).zfill(2)}:{str(req_date.minute).zfill(2)}"

def utc_time_str_to_time_str(time_str, offset_str):
    today = datetime.utcnow().date()
    in_hr, in_min = time_str.split(':')
    of_hr, of_min = offset_str[1:].split(':')
    temp_date = datetime(today.year, today.month, today.day, int(in_hr), int(in_min))
    if offset_str[0] == '-':
        req_date = temp_date - timedelta(hours=int(of_hr), minutes=int(of_min))
    else:
        req_date = temp_date + timedelta(hours=int(of_hr), minutes=int(of_min))
    return f"{str(req_date.hour).zfill(2)}:{str(req_date.minute).zfill(2)}"

def datetime_str_to_utc_datetime_str(date_str, time_str, offset_str):
    in_yr, in_mn, in_dd = date_str.split('-')
    in_hr, in_min = time_str.split(':')
    of_hr, of_min = offset_str[1:].split(':')
    temp_date = datetime(int(in_yr), int(in_mn), int(in_dd), int(in_hr), int(in_min))
    if offset_str[0] == '-':
        req_date = temp_date + timedelta(hours=int(of_hr), minutes=int(of_min))
    else:
        req_date = temp_date - timedelta(hours=int(of_hr), minutes=int(of_min))
    return req_date.date(), f"{str(req_date.hour).zfill(2)}:{str(req_date.minute).zfill(2)}"

def utc_datetime_str_to_datetime_str(date_str, time_str, offset_str):
    in_yr, in_mn, in_dd = date_str.split('-')
    in_hr, in_min = time_str.split(':')
    of_hr, of_min = offset_str[1:].split(':')
    temp_date = datetime(int(in_yr), int(in_mn), int(in_dd), int(in_hr), int(in_min))
    if offset_str[0] == '-':
        req_date = temp_date - timedelta(hours=int(of_hr), minutes=int(of_min))
    else:
        req_date = temp_date + timedelta(hours=int(of_hr), minutes=int(of_min))
    return req_date.date(), f"{str(req_date.hour).zfill(2)}:{str(req_date.minute).zfill(2)}"

def gen_random_upper_str(N=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))

def gen_random_lower_str(N=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=N))

def gen_random_str(N=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=N))

