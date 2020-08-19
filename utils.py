    
import requests
import json
from pathlib import Path
import logging

"""
    Some handy utils for doing requests and fetching from files
"""

def get(url, allow_redirects = False, params = None, bearer_token = None):
    headers=None
    if bearer_token:
        headers = {'Authorization': 'Bearer {}'.format(bearer_token)}

    logging.info("Making a GET to {} with headers {} params {}".format(url, headers, params))
    response = requests.get(url, headers=headers, allow_redirects=allow_redirects, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"GET to {url}, status code {response.status_code}")

def post(url, payload = None):
    logging.info("Making a POST to " + url)
    response = requests.post(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"POST to {url}, status code {response.status_code}")

def save_json_to_file(filename, json_to_save):
    with open(filename, 'w+') as f:
        json.dump(json_to_save, f, ensure_ascii=False, indent=4)

def get_json_from_file(dir, filename):
    Path(dir).mkdir(parents=True, exist_ok=True)
    Path(filename).touch(exist_ok=True)
    with open(filename, 'r+') as f:
        try:
            return json.load(f)
        except json.decoder.JSONDecodeError:
            logging.info("Nothing in the file")
            return None
